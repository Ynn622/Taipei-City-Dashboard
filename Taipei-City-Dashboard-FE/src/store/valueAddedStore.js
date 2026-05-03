import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import http from "../router/axios";
import {
	COMPONENT_GEOJSON_FALLBACKS,
	buildFallbackChartData,
	localSuggestion,
} from "../components/value-added/valueAddedAnalytics";

const LLM_SYSTEM_PROMPT = `你是臺北城市儀表板的食安實策分析助理。請只根據使用者提供的表格摘要、輪廓與任務回答，不要編造未提供的數字。輸出繁體中文，先給一段總結，再給 3 到 5 點可執行建議。若資料不足，必須明確指出缺口與下一步要補的資料。`;
const PROFILE_CHAT_SYSTEM_PROMPT = `你是臺北城市儀表板「實策」的輪廓訪談助理。你的任務是用自然聊天取得使用者屬於 B/C/G 哪一端，以及該端必要資訊。

三種端點：
- C 端民眾：需取得過敏原、所在地、食安敏感度類型。
- B 端業者：需取得開業內容/餐飲類別、所在地。
- G 端政府或治理使用者：需了解所在地或管轄地。

規則：
- 每次最多問 1 到 2 個缺少的重點問題。
- 不要編造使用者沒有提供的資料。
- 回覆必須只輸出 JSON，不要 markdown，不要解釋。
- JSON 格式：
{
  "reply": "給使用者看的繁體中文回覆或下一個問題",
  "profile": {
    "name": "",
    "audienceType": "B|C|G|",
    "roleLabel": "",
    "focusDistricts": [],
    "focusCategories": [],
    "allergens": [],
    "foodSafetySensitivityTypes": [],
    "businessCategory": "",
    "userLocation": null,
    "dateRangeText": "",
    "notes": "",
    "isComplete": false
  }
}`;

export const useValueAddedStore = defineStore("valueAdded", () => {
	const userProfile = reactive({
		name: "",
		audienceType: "",
		roleLabel: "",
		focusDistricts: [],
		focusCategories: [],
		allergens: [],
		foodSafetySensitivityTypes: [],
		businessCategory: "",
		userLocation: null,
		dateRangeText: "",
		notes: "",
		isComplete: false,
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

	function saveProfile(profile, options = {}) {
		Object.assign(userProfile, normalizeProfile(profile, options));
		localStorage.setItem("valueAdded_profile", JSON.stringify(userProfile));
		profileVersion.value += 1;
		llmResult.clear();
	}

	function resetProfile() {
		saveProfile({
			name: "",
			audienceType: "",
			roleLabel: "",
			focusDistricts: [],
			focusCategories: [],
			allergens: [],
			foodSafetySensitivityTypes: [],
			businessCategory: "",
			userLocation: null,
			dateRangeText: "",
			notes: "",
			isComplete: false,
		}, { preserveExisting: false });
	}

	async function fetchComponentData(id, options = {}) {
		const city = options.city || "metrotaipei";
		const timeKey = [options.time_from, options.time_to, options.dateRangeText].filter(Boolean).join(":");
		const cacheKey = `${id}:${city}:${timeKey}`;
		if (componentCache.has(cacheKey)) {
			return componentCache.get(cacheKey);
		}

		const fallbackConfig = COMPONENT_GEOJSON_FALLBACKS[id];

		try {
			const res = await http.get(`/component/${id}/chart`, {
				params: {
					city,
					time_from: options.time_from,
					time_to: options.time_to,
				},
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

	async function chatProfileAssistant(messages) {
		try {
			const res = await http.post("/ai/chat/twai", {
				session: "value_added_profile",
				stream: false,
				max_new_tokens: 700,
				temperature: 0.25,
				top_p: 0.9,
				messages: [
					{
						role: "system",
						content: PROFILE_CHAT_SYSTEM_PROMPT,
					},
					{
						role: "user",
						content: JSON.stringify({
							currentProfile: userProfile,
							conversation: messages.map(({ role, content }) => ({ role, content })),
						}, null, 2),
					},
				],
			});
			const parsed = parseProfileChatResponse(res.data?.data?.content);
			if (parsed.profile) {
				saveProfile(parsed.profile);
			}
			return parsed;
		} catch (error) {
			console.error("ValueAddedProfileChatError:", error);
			const fallback = fallbackProfileChat(messages);
			if (fallback.profile) {
				saveProfile(fallback.profile);
			}
			return fallback;
		}
	}

	function buildLLMPrompt(featureKey, profile, promptData = {}) {
		const context = promptData?.context || {};
		return JSON.stringify({
			featureKey,
			task: context.task || "實策建議",
			userProfile: {
				name: profile.name || "",
				audienceType: profile.audienceType || "",
				roleLabel: profile.roleLabel || "",
				focusDistricts: profile.focusDistricts || [],
				focusCategories: profile.focusCategories || [],
				allergens: profile.allergens || [],
				foodSafetySensitivityTypes: profile.foodSafetySensitivityTypes || [],
				businessCategory: profile.businessCategory || "",
				userLocation: profile.userLocation || null,
				dateRangeText: profile.dateRangeText || "",
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

	function parseProfileChatResponse(content) {
		const raw = String(content || "").trim();
		const jsonText = raw
			.replace(/^```(?:json)?/i, "")
			.replace(/```$/i, "")
			.trim();
		const start = jsonText.indexOf("{");
		const end = jsonText.lastIndexOf("}");
		if (start === -1 || end === -1) {
			return {
				reply: "我先幫你記下來。請告訴我你是民眾、餐飲業者，還是政府/治理單位？",
				profile: null,
			};
		}
		const parsed = JSON.parse(jsonText.slice(start, end + 1));
		return {
			reply: parsed.reply || "我了解了，請再補充所在地或主要關注的食安項目。",
			profile: parsed.profile ? normalizeProfile(parsed.profile) : null,
		};
	}

	function normalizeProfile(profile = {}, options = {}) {
		const preserveExisting = options.preserveExisting !== false;
		const normalized = {
			name: profile.name || userProfile.name || "",
			audienceType: normalizeAudienceType(profile.audienceType || userProfile.audienceType),
			roleLabel: profile.roleLabel || userProfile.roleLabel || "",
			focusDistricts: normalizeProfileList(
				profile.focusDistricts,
				userProfile.focusDistricts,
				preserveExisting
			),
			focusCategories: normalizeProfileList(
				profile.focusCategories,
				userProfile.focusCategories,
				preserveExisting
			),
			allergens: normalizeProfileList(
				profile.allergens,
				userProfile.allergens,
				preserveExisting
			),
			foodSafetySensitivityTypes: normalizeProfileList(
				profile.foodSafetySensitivityTypes,
				userProfile.foodSafetySensitivityTypes,
				preserveExisting
			),
			businessCategory: profile.businessCategory || userProfile.businessCategory || "",
			userLocation: normalizeLocation(profile.userLocation ?? userProfile.userLocation),
			dateRangeText: profile.dateRangeText ?? userProfile.dateRangeText ?? "",
			notes: profile.notes || userProfile.notes || "",
			isComplete: Boolean(profile.isComplete ?? userProfile.isComplete),
		};

		if (normalized.audienceType === "C" && normalized.foodSafetySensitivityTypes.length > 0) {
			normalized.focusCategories = normalized.foodSafetySensitivityTypes;
		}
		if (normalized.audienceType === "B" && normalized.businessCategory) {
			normalized.focusCategories = [normalized.businessCategory];
		}

		return normalized;
	}

	function normalizeLocation(value) {
		if (!value) return null;
		if (typeof value === "object") {
			const lat = Number(value.lat);
			const lng = Number(value.lng);
			return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng } : null;
		}
		const parts = String(value).split(/[,，\s]+/).map(Number).filter((item) => Number.isFinite(item));
		return parts.length >= 2 ? { lat: parts[0], lng: parts[1] } : null;
	}

	function normalizeProfileList(nextValue, currentValue, preserveExisting) {
		const nextList = normalizeList(nextValue);
		if (preserveExisting && nextValue !== undefined && nextList.length === 0) {
			return normalizeList(currentValue);
		}
		if (nextValue === undefined) {
			return normalizeList(currentValue);
		}
		return nextList;
	}

	function normalizeAudienceType(type = "") {
		const value = String(type).trim().toUpperCase();
		if (["B", "C", "G"].includes(value)) return value;
		return "";
	}

	function normalizeList(value) {
		if (Array.isArray(value)) {
			return value.map((item) => String(item).trim()).filter(Boolean);
		}
		if (!value) return [];
		return String(value)
			.split(/[,，、\s]+/)
			.map((item) => item.trim())
			.filter(Boolean);
	}

	function fallbackProfileChat(messages) {
		const latest = messages[messages.length - 1]?.content || "";
		const profile = normalizeProfile(userProfile);
		if (/民眾|消費|過敏|家人|小孩|長輩|C/i.test(latest)) {
			profile.audienceType = "C";
			profile.roleLabel = "民眾";
		} else if (/店|餐|業者|開業|營業|B/i.test(latest)) {
			profile.audienceType = "B";
			profile.roleLabel = "餐飲業者";
		} else if (/政府|機關|局處|管轄|稽查|G/i.test(latest)) {
			profile.audienceType = "G";
			profile.roleLabel = "治理單位";
		}

		const districtMatches = latest.match(/[\u4e00-\u9fa5]{1,4}[區市鎮鄉]/g);
		if (districtMatches?.length) {
			profile.focusDistricts = [...new Set([...profile.focusDistricts, ...districtMatches])];
		}
		if (profile.audienceType === "C") {
			const allergens = ["花生", "堅果", "牛奶", "蛋", "海鮮", "甲殼類", "麩質", "大豆"];
			profile.allergens = [...new Set([
				...profile.allergens,
				...allergens.filter((item) => latest.includes(item)),
			])];
		}

		return {
			reply: nextFallbackProfileQuestion(profile),
			profile,
		};
	}

	function nextFallbackProfileQuestion(profile) {
		if (!profile.audienceType) return "我先了解你的使用情境：你是民眾、餐飲業者，還是政府/治理單位？";
		if (profile.focusDistricts.length === 0) return "請告訴我你主要關注或所在的行政區。";
		if (profile.audienceType === "C" && profile.allergens.length === 0) {
			return "你或同行者有需要避開的過敏原嗎？也可以補充你最在意的食安類型。";
		}
		if (profile.audienceType === "B" && !profile.businessCategory) {
			return "你的開業內容或餐飲類別是什麼？例如便當、飲料、餐酒館或小吃。";
		}
		return "我已經先更新輪廓了，可以繼續補充其他偏好或直接關閉設定。";
	}

	loadProfile();

	return {
		userProfile,
		componentCache,
		geoJsonCache,
		llmResult,
		profileVersion,
		saveProfile,
		resetProfile,
		fetchComponentData,
		fetchGeoJsonFiles,
		fetchLLMSuggestion,
		chatProfileAssistant,
	};
});
