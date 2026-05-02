<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const featureKey = "policy-improve";

async function generate(options = {}) {
	loading.value = true;
	rows.value = rows.value?.length
		? rows.value
		: (await store.fetchComponentData(COMPONENT_IDS.healthAuditViolation)) || [];
	await store.fetchLLMSuggestion(featureKey, {
		context: {
			topItems: topRows(rows.value, 5),
			task: "政策分析改善建議",
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
