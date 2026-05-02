import { defineStore } from "pinia";
import { reactive } from "vue";
import http from "../router/axios";


export const useValueAddedStore = defineStore("valueAdded", () => {
	const userProfile = reactive({
		name: "",
		focusDistricts: [],
		focusCategories: [],
		notes: "",
	});

	const componentCache = reactive(new Map());
	const llmResult = reactive(new Map());

	function loadProfile() {
		const saved = localStorage.getItem("valueAdded_profile");
		if (saved) {
			Object.assign(userProfile, JSON.parse(saved));
		}
	}

	function saveProfile(profile) {
		Object.assign(userProfile, profile);
		localStorage.setItem("valueAdded_profile", JSON.stringify(userProfile));
	}

	async function fetchComponentData(id) {
		if (componentCache.has(id)) {
			return componentCache.get(id);
		}
		
		try {
			const res = await http.get(`/component/${id}/chart`);
			componentCache.set(id, res.data);
			return res.data;
		} catch (error) {
			console.error(error);
			return null;
		}
	}

	async function fetchLLMSuggestion(featureKey, promptData) {
		llmResult.set(featureKey, { loading: true, text: "" });
		
		try {
			const res = await http.post("/llm/suggest", {
				feature: featureKey,
				profile: userProfile,
				...promptData,
			});
			
			llmResult.set(featureKey, { loading: false, text: res.data.suggestion || res.data.text || "" });
		} catch (error) {
			console.error(error);
			llmResult.set(featureKey, { loading: false, text: "無法取得 LLM 建議，請稍後再試。" });
		}
	}

	loadProfile();

	return {
		userProfile,
		componentCache,
		llmResult,
		saveProfile,
		fetchComponentData,
		fetchLLMSuggestion,
	};
});
