<script setup>
import { computed, onMounted, ref } from "vue";
import VueApexCharts from "vue3-apexcharts";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, computePeriodDelta, formatNumber } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const violationRows = ref([]);

onMounted(async () => {
	violationRows.value = await store.fetchComponentData(COMPONENT_IDS.healthAuditViolation);
	loading.value = false;
});

const priorities = computed(() => computePeriodDelta(violationRows.value, { limit: 6 }));
const chartSeries = computed(() => [
	{
		name: "違規增加",
		data: priorities.value.map((item) => ({
			x: item.label,
			y: item.delta,
			fillColor: item.delta >= 0 ? "#E86F51" : "#30B68F",
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
			horizontal: true,
			borderRadius: 3,
			distributed: true,
		},
	},
	grid: { show: false },
	legend: { show: false },
	dataLabels: {
		enabled: true,
		formatter: (value) => `${value >= 0 ? "+" : ""}${Math.round(value)}`,
		style: {
			colors: ["#fff"],
			fontSize: "11px",
		},
	},
	xaxis: {
		labels: { show: false },
		axisTicks: { show: false },
		axisBorder: { show: false },
	},
	yaxis: {
		labels: {
			style: {
				colors: "#b8b8b8",
				fontSize: "12px",
			},
		},
	},
	tooltip: {
		theme: "dark",
		y: {
			formatter: (value) => `${value >= 0 ? "+" : ""}${Math.round(value)} 件`,
		},
	},
}));
</script>

<template>
  <ValueAddedCard
    title="稽查優先排序"
    subtitle="依上月到本月違規增加幅度排名，優先看增幅明顯區域。"
    :loading="loading"
  >
    <div class="priority-chart">
      <VueApexCharts
        type="bar"
        height="210"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>
    <div class="priority-list">
      <div
        v-for="item in priorities"
        :key="item.label"
      >
        <span>#{{ item.rank }} {{ item.label }}</span>
        <strong>{{ item.delta >= 0 ? "+" : "" }}{{ formatNumber(item.delta, " 件") }}</strong>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.priority-chart {
  min-height: 210px;
  margin: -0.4rem 0 -0.2rem;
}

.priority-list {
  display: grid;
  gap: 0.55rem;

  div {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    padding: 0.68rem;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.045);
  }

  span {
    color: var(--color-normal-text);
    font-weight: 800;
  }

  strong {
    color: #E86F51;
  }
}
</style>
