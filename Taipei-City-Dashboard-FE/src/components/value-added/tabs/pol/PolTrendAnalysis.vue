<script setup>
import { computed, onMounted, ref } from "vue";
import VueApexCharts from "vue3-apexcharts";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, computePeriodDelta, formatNumber } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const foodRows = ref([]);
const healthRows = ref([]);
const infectiousRows = ref([]);

onMounted(async () => {
	const [food, health, infectious] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.infectious),
	]);
	foodRows.value = food;
	healthRows.value = health;
	infectiousRows.value = infectious;
	loading.value = false;
});

const factors = computed(() => [
	...computePeriodDelta(foodRows.value, { groupKey: "product_category", limit: 4 }).map((item) => ({ ...item, type: "食品違規" })),
	...computePeriodDelta(healthRows.value, { limit: 4 }).map((item) => ({ ...item, type: "環境違規" })),
	...computePeriodDelta(infectiousRows.value, { limit: 4 }).map((item) => ({ ...item, type: "就診趨勢" })),
].sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 6));
const chartSeries = computed(() => [
	{
		name: "變動量",
		data: factors.value.map((item) => ({
			x: `${item.type} ${item.label}`,
			y: item.delta,
			fillColor: colorByType(item.type),
		})),
	},
]);
const chartOptions = computed(() => ({
	chart: {
		type: "bar",
		toolbar: { show: false },
		background: "transparent",
	},
	plotOptions: {
		bar: {
			borderRadius: 3,
			distributed: true,
			columnWidth: "48%",
		},
	},
	grid: {
		borderColor: "rgba(255, 255, 255, 0.08)",
		strokeDashArray: 3,
	},
	legend: { show: false },
	dataLabels: { enabled: false },
	xaxis: {
		labels: {
			rotate: -28,
			trim: true,
			style: {
				colors: "#b8b8b8",
				fontSize: "11px",
			},
		},
		axisTicks: { show: false },
		axisBorder: { color: "rgba(255, 255, 255, 0.12)" },
	},
	yaxis: {
		labels: {
			style: {
				colors: "#b8b8b8",
				fontSize: "11px",
			},
		},
	},
	tooltip: {
		theme: "dark",
		y: {
			formatter: (value) => `${value >= 0 ? "+" : ""}${Math.round(value)}`,
		},
	},
}));

function colorByType(type) {
	if (type === "食品違規") return "#E86F51";
	if (type === "環境違規") return "#D84C73";
	return "#F2C94C";
}
</script>

<template>
  <ValueAddedCard
    title="趨勢分析"
    subtitle="以時間因子排行榜呈現食品、環境與就診指標的最大變動。"
    :loading="loading"
  >
    <div class="trend-chart">
      <VueApexCharts
        type="bar"
        height="230"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>
    <div class="factor-list">
      <div
        v-for="item in factors"
        :key="`${item.type}-${item.label}`"
      >
        <small>{{ item.type }}</small>
        <span>{{ item.label }}</span>
        <strong>{{ item.delta >= 0 ? "+" : "" }}{{ formatNumber(item.delta) }}</strong>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.trend-chart {
  min-height: 230px;
  margin: -0.35rem 0 -0.1rem;
}

.factor-list {
  display: grid;
  gap: 0.55rem;

  div {
    display: grid;
    grid-template-columns: 78px minmax(0, 1fr) auto;
    gap: 0.6rem;
    align-items: center;
    padding: 0.62rem;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.045);
  }

  small {
    color: var(--color-complement-text);
  }

  span {
    color: var(--color-normal-text);
    font-weight: 700;
  }

  strong {
    color: #F2C94C;
  }
}
</style>
