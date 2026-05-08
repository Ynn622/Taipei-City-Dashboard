<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, computeFoodSafetyRisk, formatNumber, sumRows, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const helpRows = ref([]);
const violationRows = ref([]);

onMounted(async () => {
	const [help, foodAudit, healthAudit] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthOffice),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
	]);
	helpRows.value = help;
	violationRows.value = [...topRows(foodAudit, 99), ...topRows(healthAudit, 99)];
	loading.value = false;
});

const risk = computed(() => computeFoodSafetyRisk({
	support: sumRows(helpRows.value),
	violations: sumRows(violationRows.value),
}));
</script>

<template>
  <ValueAddedCard
    title="食安風險計算"
    subtitle="以支援據點與違規數量計算可解釋的營運食安風險。"
    :loading="loading"
  >
    <div class="risk-score">
      <strong>{{ risk.score }}</strong>
      <span>{{ risk.level }}</span>
    </div>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          支援據點
        </div>
        <div class="summary-value">
          {{ formatNumber(risk.support, " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          違規數量
        </div>
        <div class="summary-value">
          {{ formatNumber(risk.violations, " 件") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          風險等級
        </div>
        <div class="summary-value">
          {{ risk.level }}
        </div>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.risk-score {
  display: grid;
  place-items: center;
  min-height: 120px;
  border-radius: 8px;
  background: rgba(48, 182, 143, 0.1);
  border: solid 1px rgba(255, 255, 255, 0.09);

  strong {
    color: var(--color-normal-text);
    font-size: 3rem;
    line-height: 1;
  }

  span {
    color: var(--color-complement-text);
    font-weight: 800;
  }
}
</style>
