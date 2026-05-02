import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import http from "../router/axios";
import {
	COMPONENT_GEOJSON_FALLBACKS,
	buildFallbackChartData,
	localSuggestion,
} from "../components/value-added/valueAddedAnalytics";


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
		if (fallbackConfig && !options.preferApi) {
			const collections = await fetchGeoJsonFiles(fallbackConfig.files);
			const fallbackData = buildFallbackChartData(id, collections);
			componentCache.set(cacheKey, fallbackData);
			return fallbackData;
		}
		
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

	async function fetchLLMSuggestion(featureKey, promptData) {
		llmResult.set(featureKey, { loading: true, text: "" });

		llmResult.set(featureKey, {
			loading: false,
			text: localSuggestion(featureKey, userProfile, promptData?.context),
			fallback: true,
		});
		return llmResult.get(featureKey);
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
