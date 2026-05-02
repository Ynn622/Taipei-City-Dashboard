<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const violationRows = ref([]);
const restaurantRows = ref([]);

onMounted(async () => {
	const [violations, restaurants] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.goodRestaurants),
	]);
	violationRows.value = violations;
	restaurantRows.value = restaurants;
	loading.value = false;
});

const priorities = computed(() => {
	const restaurantMap = new Map(topRows(restaurantRows.value, 99).map((item) => [item.label, item.value]));
	return topRows(violationRows.value, 6)
		.map((item) => ({
			...item,
			value: Math.max(Math.round(item.value - (restaurantMap.get(item.label) || 0) * 0.2), 0),
		}))
		.sort((a, b) => b.value - a.value)
		.slice(0, 6);
});

const chartOptions = computed(() => ({
	chart: { type: "bar", background: "transparent", toolbar: { show: false }, fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: ["#D84C73", "#E86F51", "#F2994A", "#F2C94C", "#1E88E5", "#72C6A4"],
	plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: true } },
	dataLabels: { enabled: true, formatter: (v) => v + " 分", style: { fontSize: "11px", colors: ["#fff"] } },
	grid: { borderColor: "#494b4e", xaxis: { lines: { show: true } }, yaxis: { lines: { show: false } } },
	xaxis: {
		categories: priorities.value.map((r) => r.label),
		labels: { style: { colors: "#888787", fontSize: "11px" } },
		axisBorder: { show: false }, axisTicks: { show: false },
	},
	yaxis: { labels: { style: { colors: "#fff", fontSize: "11px", fontWeight: 600 } } },
	legend: { show: false },
	tooltip: { theme: "dark", y: { formatter: (v) => v + " 分" } },
}));

const chartSeries = computed(() => [{ name: "稽查優先分數", data: priorities.value.map((r) => r.value) }]);
</script>

<template>
  <ValueAddedCard
    title="稽查優先排序"
    subtitle="違規量扣除優良餐廳覆蓋度，數字愈高代表愈需優先稽查。"
    :loading="loading"
  >
    <apexchart
      v-if="!loading && chartSeries[0].data.length"
      type="bar"
      width="100%"
      height="230"
      :options="chartOptions"
      :series="chartSeries"
    />
  </ValueAddedCard>
</template>
