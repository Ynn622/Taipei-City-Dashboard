<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.foodAuditViolation);
	loading.value = false;
});

const dangerSources = computed(() => topRows(rows.value, 6));

const RISK_COLORS = ["#D84C73", "#E86F51", "#F2994A", "#F2C94C", "#30B68F", "#72C6A4"];

const chartOptions = computed(() => ({
	chart: { type: "donut", background: "transparent", fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: RISK_COLORS,
	labels: dangerSources.value.map((r) => r.label),
	dataLabels: {
		enabled: true,
		formatter: (val, { seriesIndex, w }) => w.globals.labels[seriesIndex],
		style: { fontSize: "11px", fontWeight: 600 },
		dropShadow: { enabled: false },
	},
	stroke: { colors: ["#282a2c"], width: 3 },
	plotOptions: {
		pie: {
			donut: { size: "72%", labels: { show: true, total: { show: true, label: "最高風險", fontSize: "12px", color: "#888787", formatter: () => dangerSources.value[0]?.label || "" } } },
		},
	},
	legend: { position: "bottom", labels: { colors: "#888787" }, fontSize: "12px" },
	tooltip: { theme: "dark", y: { formatter: (v) => `${v} 件` } },
}));

const chartSeries = computed(() => dangerSources.value.map((r) => r.value));
</script>

<template>
  <ValueAddedCard
    title="危險來源迴避"
    subtitle="以食品抽驗不合格分布提示應避開或加強查核的來源。"
    :loading="loading"
  >
    <apexchart
      v-if="!loading && chartSeries.length"
      type="donut"
      width="100%"
      height="240"
      :options="chartOptions"
      :series="chartSeries"
    />
    <p class="note">
      若採購來源位於高違規區，建議提高進貨批次抽驗比例並保留替代廠商。
    </p>
  </ValueAddedCard>
</template>
