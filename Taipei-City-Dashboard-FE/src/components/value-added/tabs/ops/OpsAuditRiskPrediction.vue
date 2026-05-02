<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	filterByProfileDistrict,
	formatNumber,
	sumRows,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const healthRows = ref([]);
const foodRows = ref([]);

onMounted(async () => {
	const [health, food] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
	]);
	healthRows.value = health;
	foodRows.value = food;
	loading.value = false;
});

const scopedRows = computed(() => [
	...filterByProfileDistrict(healthRows.value, store.userProfile),
	...filterByProfileDistrict(foodRows.value, store.userProfile),
]);
const risks = computed(() => topRows(scopedRows.value, 6));

const chartOptions = computed(() => ({
	chart: { type: "bar", background: "transparent", toolbar: { show: false }, fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: risks.value.map((_, i) => {
		const palette = ["#D84C73", "#E86F51", "#F2994A", "#F2C94C", "#30B68F", "#72C6A4"];
		return palette[i] || "#888787";
	}),
	plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: true } },
	dataLabels: { enabled: true, formatter: (v) => `${v} 件`, style: { fontSize: "11px", colors: ["#fff"] } },
	grid: { borderColor: "#494b4e", xaxis: { lines: { show: true } }, yaxis: { lines: { show: false } } },
	xaxis: {
		categories: risks.value.map((r) => r.label),
		labels: { style: { colors: "#888787", fontSize: "11px" } },
		axisBorder: { show: false }, axisTicks: { show: false },
	},
	yaxis: { labels: { style: { colors: "#fff", fontSize: "11px", fontWeight: 600 } } },
	legend: { show: false },
	tooltip: { theme: "dark", y: { formatter: (v) => `${v} 件` } },
}));

const chartSeries = computed(() => [
	{ name: "違規件數", data: risks.value.map((r) => r.value) },
]);
</script>

<template>
  <ValueAddedCard
    title="稽查風險預測"
    subtitle="整合衛生與食品稽核違規，推估近期需優先注意的行政區。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          輪廓範圍違規
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(scopedRows), " 件") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          最高風險區
        </div>
        <div class="summary-value">
          {{ risks[0]?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          建議稽查等級
        </div>
        <div class="summary-value">
          {{ sumRows(scopedRows) > 80 ? "高" : "中" }}
        </div>
      </div>
    </div>
    <apexchart
      v-if="!loading && chartSeries[0].data.length"
      type="bar"
      width="100%"
      height="200"
      :options="chartOptions"
      :series="chartSeries"
    />
  </ValueAddedCard>
</template>
