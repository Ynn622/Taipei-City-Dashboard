import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import http from "../router/axios";
import {
	COMPONENT_GEOJSON_FALLBACKS,
	buildFallbackChartData,
	localSuggestion,
} from "../components/value-added/valueAddedAnalytics";

const LLM_SYSTEM_PROMPT = `你是臺北城市儀表板的食安加值服務分析助理。請只根據使用者提供的資料摘要、輪廓與任務回答，不要編造未提供的數字。輸出繁體中文，給 3 到 5 點可執行建議，語氣專業精簡。`;

export const useValueAddedStore = defineStore("valueAdded", () => {
	const userProfile = reactive({
		name: "",
		focusDistricts: [],
		focusCategories: [],
		notes: "",
	});

	const componentCache = reactive(new Map());
	const geoJsonCache = reactive(new Map());
	const llmResult = reactive(new Map());
	const profileVersion = ref(0);

	function loadProfile() {
		const saved = localStorage.getItem("valueAdded_profile");
		if (saved) {
			try {
				Object.assign(userProfile, JSON.parse(saved));
			} catch (error) {
				console.error("ValueAddedProfileParseError:", error);
			}
		}
	}

	function saveProfile(profile) {
		Object.assign(userProfile, profile);
		localStorage.setItem("valueAdded_profile", JSON.stringify(userProfile));
		profileVersion.value += 1;
		llmResult.clear();
	}

	async function fetchComponentData(id, options = {}) {
		const city = options.city || "metrotaipei";
		const cacheKey = `${id}:${city}`;
		if (componentCache.has(cacheKey)) {
			return componentCache.get(cacheKey);
		}

		const fallbackConfig = COMPONENT_GEOJSON_FALLBACKS[id];

		try {
			const res = await http.get(`/component/${id}/chart`, {
				params: { city },
			});
			componentCache.set(cacheKey, res.data);
			return res.data;
		} catch (error) {
			console.error("ValueAddedComponentFetchError:", error);
			if (!fallbackConfig) return null;

			const collections = await fetchGeoJsonFiles(fallbackConfig.files);
			const fallbackData = buildFallbackChartData(id, collections);
			componentCache.set(cacheKey, fallbackData);
			return fallbackData;
		}
	}

	async function fetchGeoJson(fileName) {
		if (geoJsonCache.has(fileName)) {
			return geoJsonCache.get(fileName);
		}

		try {
			const res = await fetch(`/mapData/${fileName}`);
			if (!res.ok) throw new Error(`${res.status} ${fileName}`);
			const data = await res.json();
			geoJsonCache.set(fileName, data);
			return data;
		} catch (error) {
			console.error("ValueAddedGeoJsonFetchError:", error);
			geoJsonCache.set(fileName, null);
			return null;
		}
	}

	async function fetchGeoJsonFiles(fileNames) {
		const results = await Promise.all(fileNames.map((fileName) => fetchGeoJson(fileName)));
		return results.filter(Boolean);
	}

	async function fetchLLMSuggestion(featureKey, promptData, options = {}) {
		const cachedResult = llmResult.get(featureKey);
		if (!options.force && cachedResult?.text) {
			return cachedResult;
		}

		llmResult.set(featureKey, { loading: true, text: "" });

		try {
			const res = await http.post("/ai/chat/twai", {
				session: `value_added_${featureKey}`,
				stream: false,
				max_new_tokens: 600,
				temperature: 0.35,
				top_p: 0.9,
				messages: [
					{
						role: "system",
						content: LLM_SYSTEM_PROMPT,
					},
					{
						role: "user",
						content: buildLLMPrompt(featureKey, userProfile, promptData),
					},
				],
			});
			llmResult.set(featureKey, {
				loading: false,
				text: res.data?.data?.content || localSuggestion(featureKey, userProfile, promptData?.context),
				fallback: false,
			});
		} catch (error) {
			console.error("ValueAddedLLMFetchError:", error);
			llmResult.set(featureKey, {
				loading: false,
				text: localSuggestion(featureKey, userProfile, promptData?.context),
				fallback: true,
				error: error?.response?.data?.message || error?.message || "LLM request failed",
			});
		}
		return llmResult.get(featureKey);
	}

	function buildLLMPrompt(featureKey, profile, promptData = {}) {
		const context = promptData?.context || {};
		return JSON.stringify({
			featureKey,
			task: context.task || "加值服務建議",
			userProfile: {
				name: profile.name || "",
				focusDistricts: profile.focusDistricts || [],
				focusCategories: profile.focusCategories || [],
				notes: profile.notes || "",
			},
			dataContext: context,
			requirements: [
				"只使用 dataContext 中提供的資料與趨勢。",
				"若資料不足，明確說明需要補哪些資料。",
				"建議須可直接轉成查核、追蹤、公告或供應替代方案。",
			],
		}, null, 2);
	}

	loadProfile();

	return {
		userProfile,
		componentCache,
		geoJsonCache,
		llmResult,
		profileVersion,
		saveProfile,
		fetchComponentData,
		fetchGeoJsonFiles,
		fetchLLMSuggestion,
	};
});
