<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../store/valueAddedStore";
import {
	COMPONENT_IDS,
	highRiskAreaComparison,
	metricComparison,
	rowLabel,
	unwrapRows,
} from "./valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const datasets = ref({
	healthAudit: [],
	foodAudit: [],
	foodSource: [],
	infectious: [],
});

onMounted(async () => {
	const [healthAudit, foodAudit, foodSource, infectious] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.foodSource),
		store.fetchComponentData(COMPONENT_IDS.infectious),
	]);
	datasets.value = { healthAudit, foodAudit, foodSource, infectious };
	loading.value = false;
});

const metrics = computed(() => {
	const allViolationRows = [
		...rowsForMetric(datasets.value.healthAudit),
		...rowsForMetric(datasets.value.foodAudit),
	];
	const violationRows = filterRowsByProfile(allViolationRows);
	const violations = metricComparison(
		{ rawRows: violationRows },
		{ unit: " 件", mode: "length" }
	);
	const highRiskAreas = highRiskAreaComparison({ rawRows: violationRows }, 1);
	const suppliers = metricComparison(datasets.value.foodSource, {
		unit: " 處",
		mode: "length",
		static: true,
	});
	const diarrhea = metricComparison(datasets.value.infectious, {
		unit: " 人次",
	});

	return [
		{
			label: "雙北違規總數",
			id: "violation-total",
			...violations,
		},
		{
			label: "高風險區域數",
			id: "high-risk-areas",
			...highRiskAreas,
		},
		{
			label: "優良農場供應商數",
			id: "good-farms",
			...suppliers,
		},
		{
			label: "近期腹瀉就診趨勢",
			id: "diarrhea-trend",
			...diarrhea,
		},
	];
});

function rowsForMetric(payload) {
	return Array.isArray(payload?.rawRows) ? payload.rawRows : unwrapRows(payload);
}

function filterRowsByProfile(rows) {
	const districts = Array.isArray(store.userProfile.focusDistricts)
		? store.userProfile.focusDistricts.filter(Boolean)
		: [];
	if (districts.length === 0) return rows;
	return rows.filter((row) => districts.includes(rowLabel(row)));
}
</script>

<template>
  <div class="metrics-bar">
    <div
      v-for="metric in metrics"
      :key="metric.id"
      class="metric-card"
    >
      <div class="metric-label">
        {{ metric.label }}
      </div>
      <div
        v-if="loading"
        class="metric-loading"
      >
        載入中...
      </div>
      <div
        v-else
        class="metric-comparison"
      >
        <div class="comparison-row primary">
          <span>本週</span>
          <strong>{{ metric.currentText }}</strong>
        </div>
        <div class="comparison-row">
          <span>上週</span>
          <strong>{{ metric.previousText }}</strong>
        </div>
        <div
          class="comparison-row delta"
          :class="{
            up: metric.delta > 0,
            down: metric.delta < 0,
            muted: !metric.canCompare,
          }"
        >
          <span>差異</span>
          <strong>{{ metric.deltaText }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.metrics-bar {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  height: 100%;

  .metric-card {
    min-width: 0;
    min-height: 112px;
    background: var(--color-component-background);
    border: solid 1px var(--color-border);
    padding: 0.82rem;
    border-radius: 5px;
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-left: solid 3px var(--card-theme, var(--color-highlight));

    &:nth-child(1) { --card-theme: #E86F51; }
    &:nth-child(2) { --card-theme: #F5B041; }
    &:nth-child(3) { --card-theme: #30B68F; }
    &:nth-child(4) { --card-theme: #1E88E5; }

    .metric-label {
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--color-complement-text);
      margin-bottom: 0.35rem;
    }

    .metric-loading {
      color: var(--color-complement-text);
      font-size: 0.92rem;
      display: flex;
      align-items: center;
      height: 100%;
    }

    .metric-comparison {
      display: flex;
      flex-direction: column;
      gap: 0.26rem;
    }

    .comparison-row {
      display: flex;
      justify-content: space-between;
      gap: 0.75rem;
      align-items: baseline;
      color: var(--color-complement-text);
      font-size: 0.74rem;

      strong {
        min-width: 0;
        color: var(--color-normal-text);
        font-size: 0.88rem;
        text-align: right;
        overflow-wrap: anywhere;
      }

      &.primary {
        strong {
          font-size: 1.18rem;
          font-weight: 700;
          color: var(--card-theme);
        }
      }

      &.delta {
        margin-top: 0.15rem;
        padding-top: 0.32rem;
        border-top: solid 1px rgba(255, 255, 255, 0.06);

        strong {
          color: var(--color-complement-text);
          font-weight: 600;
        }
        &.up strong { color: #E86F51; }
        &.down strong { color: #30B68F; }
      }
    }
  }
}

@media (max-width: 640px) {
  .metrics-bar {
    grid-template-columns: 1fr;
  }
}
</style>
