<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.postHelpAgency);
	loading.value = false;
});

const helpTypes = computed(() => topRows(rows.value, 5));

const chartOptions = computed(() => ({
	chart: { type: "bar", background: "transparent", toolbar: { show: false }, fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: ["#30B68F"],
	plotOptions: {
		bar: {
			horizontal: true,
			borderRadius: 4,
			barHeight: "58%",
		},
	},
	dataLabels: {
		enabled: true,
		formatter: (value) => formatNumber(value, " 處"),
		style: { fontSize: "11px", fontWeight: 700, colors: ["#fff"] },
	},
	grid: {
		borderColor: "#494b4e",
		xaxis: { lines: { show: true } },
		yaxis: { lines: { show: false } },
	},
	xaxis: {
		categories: helpTypes.value.map((item) => item.label),
		labels: { style: { colors: "#888787", fontSize: "11px" } },
		axisBorder: { show: false },
		axisTicks: { show: false },
	},
	yaxis: {
		labels: {
			style: { colors: "#fff", fontSize: "11px", fontWeight: 600 },
		},
	},
	legend: { show: false },
	tooltip: {
		theme: "dark",
		y: { formatter: (value) => formatNumber(value, " 處") },
	},
}));

const chartSeries = computed(() => [
	{ name: "支援節點", data: helpTypes.value.map((item) => item.value) },
]);
</script>

<template>
  <ValueAddedCard
    title="快速求助"
    subtitle="彙整醫療、申訴與消費爭議支援節點。"
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
    <p class="note">
      發生疑似食安事件時，先就醫保留診斷與消費憑證，再依所在地向衛生局或消保單位通報。
    </p>
  </ValueAddedCard>
</template>
