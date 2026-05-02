<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.foodSource);
	loading.value = false;
});

const recommended = computed(() => topRows(rows.value, 8));

const chartOptions = computed(() => ({
	chart: { type: "bar", background: "transparent", toolbar: { show: false }, fontFamily: "inherit" },
	theme: { mode: "dark" },

	plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: true } },
	colors: ["#30B68F", "#72C6A4", "#1E88E5", "#F2C94C", "#F2994A", "#E86F51", "#B8325A", "#D84C73"],
	dataLabels: { enabled: false },
	grid: { borderColor: "#494b4e", xaxis: { lines: { show: true } }, yaxis: { lines: { show: false } } },
	xaxis: {
		categories: recommended.value.map((r) => r.label),
		labels: { style: { colors: "#888787", fontSize: "11px" } },
		axisBorder: { show: false },
		axisTicks: { show: false },
	},
	yaxis: { labels: { style: { colors: "#888787", fontSize: "11px" } } },
	tooltip: { theme: "dark", y: { formatter: (v) => `${v} 處` } },
	legend: { show: false },
}));

const chartSeries = computed(() => [
	{ name: "有機農場供應數", data: recommended.value.map((r) => r.value) },
]);
</script>

<template>
  <ValueAddedCard
    title="安全供應來源推薦"
    subtitle="依有機農場供應來源分布，優先推薦可替代採購區域。"
    :loading="loading"
  >
    <apexchart
      v-if="!loading && chartSeries[0].data.length"
      type="bar"
      width="100%"
      height="220"
      :options="chartOptions"
      :series="chartSeries"
    />
  </ValueAddedCard>
</template>
