<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../store/valueAddedStore";
import {
	COMPONENT_IDS,
	metricComparison,
} from "./valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const datasets = ref({
	infectious: [],
});

onMounted(async () => {
	const infectious = await store.fetchComponentData(COMPONENT_IDS.infectious);
	datasets.value = { infectious };
	loading.value = false;
});

const metrics = computed(() => {
	const diarrhea = metricComparison(datasets.value.infectious, {
		unit: " 人次",
		seriesNames: ["門診", "住院", "急診"],
		emptyText: "無資料",
	});

	return [
		{
			label: "近期腹瀉就診趨勢",
			id: "diarrhea-trend",
			icon: "show_chart",
			...diarrhea,
		},
	];
});
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
          <span>{{ metric.currentLabelText || "最新" }}</span>
        </div>
        <div class="metric-footer">
          <div class="comparison-row previous">
            <span>{{ metric.previousLabelText || "比較" }}</span>
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
  grid-template-columns: minmax(0, 1fr);
  gap: 0.8rem;
  height: 100%;

  .metric-card {
    position: relative;
    min-width: 0;
    min-height: 128px;
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
      gap: 0.68rem;
    }

    .metric-footer {
      display: grid;
      grid-template-columns: 1fr;
      gap: 0.55rem;
      align-items: stretch;
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
        flex-direction: column;
        align-items: flex-start;
        justify-content: flex-start;
        gap: 0.7rem;

        strong {
          font-size: 1.38rem;
          font-weight: 700;
          color: var(--color-normal-text);
          line-height: 1.08;
        }
      }

      &.previous {
        justify-content: center;
        padding: 0.42rem 0.5rem;
        border-radius: 7px;
        background: rgba(255, 255, 255, 0.035);
      }

      &.delta {
        justify-content: center;
        min-height: 48px;
        padding: 0.48rem 0.62rem;
        border: solid 1px rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.055);

        span {
          font-size: 0.78rem;
          font-weight: 700;
          color: var(--color-normal-text);
        }

        strong {
          color: var(--color-complement-text);
          font-size: 1.28rem;
          font-weight: 800;
          line-height: 1.05;
        }
        &.up strong { color: #E86F51; }
        &.down strong { color: #30B68F; }

        &.muted {
          span {
            color: var(--color-complement-text);
          }

          strong {
            color: var(--color-complement-text);
            font-size: 1.08rem;
          }
        }
      }
    }
  }
}

@media (max-width: 640px) {
  .metrics-bar {
    grid-template-columns: 1fr;

    .metric-card {
      min-height: 128px;
    }

    .metric-card .metric-footer {
      grid-template-columns: 1fr;
    }
  }
}
</style>
