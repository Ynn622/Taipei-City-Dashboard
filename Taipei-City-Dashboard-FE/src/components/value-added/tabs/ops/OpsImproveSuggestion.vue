<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const featureKey = "operations-improve";

async function generate(options = {}) {
	loading.value = true;
	rows.value = rows.value?.length
		? rows.value
		: (await store.fetchComponentData(COMPONENT_IDS.foodSource)) || [];
	await store.fetchLLMSuggestion(featureKey, {
		context: {
			topItems: topRows(rows.value, 5),
			task: "營運管理改善建議",
		},
	}, options);
	loading.value = false;
}

onMounted(generate);
watch(() => store.profileVersion, () => generate({ force: true }));

const result = computed(() => store.llmResult.get(featureKey));
</script>

<template>
  <ValueAddedCard
    title="LLM 改善建議"
    subtitle="根據用戶輪廓與供應來源資料產生營運改善重點。"
    :loading="loading || result?.loading"
    wide
  >
    <template #action>
      <button
        class="action-btn"
        @click="generate({ force: true })"
      >
        重新產生
      </button>
    </template>
    <p class="suggestion">
      {{ result?.text }}
    </p>
  </ValueAddedCard>
</template>
