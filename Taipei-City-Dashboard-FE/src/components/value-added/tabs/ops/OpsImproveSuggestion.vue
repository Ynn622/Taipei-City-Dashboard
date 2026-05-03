<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	buildSummaryContext,
	computeFoodSafetyRisk,
	computePeriodDelta,
	sortByDistanceThenDistrict,
	sumRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const context = ref(null);
const featureKey = "operations-improve";

async function generate(options = {}) {
	loading.value = true;
	const [source, foodAudit, healthAudit, help] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.foodSource),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.healthOffice),
	]);
	context.value = buildSummaryContext("營運管理總結", {
		nearestSuppliers: sortByDistanceThenDistrict(source, store.userProfile.userLocation, {
			fallbackDistricts: store.userProfile.focusDistricts,
		}).slice(0, 5),
		avoidFoods: computePeriodDelta(foodAudit, { groupKey: "product_category", limit: 5 }),
		auditRisk: computePeriodDelta([...computePeriodDelta(foodAudit, { limit: 99 }), ...computePeriodDelta(healthAudit, { limit: 99 })], { limit: 5 }),
		foodSafetyRisk: computeFoodSafetyRisk({
			support: sumRows(help),
			violations: sumRows(foodAudit) + sumRows(healthAudit),
		}),
	});
	await store.fetchLLMSuggestion(featureKey, {
		context: {
			...context.value,
			task: "營運管理改善建議：先總結，再列 3-5 條可執行行動。",
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
