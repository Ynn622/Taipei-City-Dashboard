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
			icon: "warning",
			...violations,
		},
		{
			label: "高風險區域數",
			id: "high-risk-areas",
			icon: "location_on",
			...highRiskAreas,
		},
		{
			label: "優良農場供應商數",
			id: "good-farms",
			icon: "verified",
			...suppliers,
		},
		{
			label: "近期腹瀉就診趨勢",
			id: "diarrhea-trend",
			icon: "show_chart",
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
      <div class="metric-topline">
        <span class="metric-icon">{{ metric.icon }}</span>
        <div class="metric-label">
          {{ metric.label }}
        </div>
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
          <strong>{{ metric.currentText }}</strong>
          <span>本週</span>
        </div>
        <div class="metric-footer">
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
  </div>
</template>

<style scoped lang="scss">
.metrics-bar {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
  height: 100%;

  .metric-card {
    position: relative;
    min-width: 0;
    min-height: 119px;
    overflow: hidden;
    background: var(--color-component-background);
    border: solid 1px rgba(255, 255, 255, 0.09);
    padding: 0.88rem;
    border-radius: 8px;
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);

    .metric-topline {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: 0;
    }

    .metric-icon {
      width: 30px;
      height: 30px;
      flex: 0 0 30px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--color-normal-text);
      font-family: var(--font-icon);
      font-size: 1.05rem;
    }

    .metric-label {
      min-width: 0;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--color-complement-text);
      line-height: 1.35;
      overflow-wrap: anywhere;
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
      gap: 0.55rem;
    }

    .metric-footer {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.4rem;
    }

    .comparison-row {
      display: flex;
      flex-direction: column;
      gap: 0.08rem;
      min-width: 0;
      color: var(--color-complement-text);
      font-size: 0.74rem;

      strong {
        min-width: 0;
        color: var(--color-normal-text);
        font-size: 0.86rem;
        text-align: left;
        overflow-wrap: anywhere;
      }

      &.primary {
        flex-direction: row;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.7rem;

        strong {
          font-size: 1.38rem;
          font-weight: 700;
          color: var(--color-normal-text);
          line-height: 1.08;
        }
      }

      &.delta {
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

    .metric-card {
      min-height: 110px;
    }
  }
}
</style>
