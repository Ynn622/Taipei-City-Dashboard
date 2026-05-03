<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, buildSummaryContext, computePeriodDelta, rankRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const context = ref(null);
const featureKey = "policy-improve";

async function generate(options = {}) {
	loading.value = true;
	const [healthAudit, foodAudit, market, water] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.market),
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
	]);
	context.value = buildSummaryContext("政策分析總結", {
		riskHotspots: rankRows(healthAudit, { limit: 6 }),
		auditPriority: computePeriodDelta(healthAudit, { limit: 6 }),
		trendFactors: [
			...computePeriodDelta(foodAudit, { groupKey: "product_category", limit: 4 }),
			...computePeriodDelta(water, { limit: 4 }),
		],
		eventScope: rankRows(market, { limit: 4 }),
	});
	await store.fetchLLMSuggestion(featureKey, {
		context: {
			...context.value,
			task: "政策分析改善建議：先總結，再列政策優先事項。",
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
    subtitle="依據熱區與政策稽查優先序，整理可執行治理建議。"
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
