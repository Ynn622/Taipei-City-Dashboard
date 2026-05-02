<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, sumRows, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const waterRows = ref([]);
const officeRows = ref([]);

onMounted(async () => {
	const [water, offices] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
		store.fetchComponentData(COMPONENT_IDS.healthOffice),
	]);
	waterRows.value = water;
	officeRows.value = offices;
	loading.value = false;
});

const estimate = computed(() => {
	const waterLoad = sumRows(waterRows.value);
	const officeCount = Math.max(sumRows(officeRows.value), 1);
	const exposure = Math.round(waterLoad / officeCount);
	return {
		waterLoad,
		officeCount,
		exposure,
		level: exposure > 30 ? "偏高" : exposure > 12 ? "中等" : "穩定",
		percent: Math.min(Math.round((exposure / 50) * 100), 100),
	};
});

const officeTypes = computed(() => topRows(officeRows.value, 4));

const gaugeOptions = computed(() => ({
	chart: { type: "radialBar", background: "transparent", fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: estimate.value.percent > 60 ? ["#D84C73"] : estimate.value.percent > 30 ? ["#F5B041"] : ["#30B68F"],
	plotOptions: {
		radialBar: {
			hollow: { size: "60%" },
			dataLabels: {
				name: { show: true, fontSize: "13px", color: "#888787", offsetY: -8 },
				value: { show: true, fontSize: "1.4rem", fontWeight: 800, color: "#fff", offsetY: 4, formatter: () => estimate.value.level },
			},
		},
	},
	labels: ["曝險等級"],
}));

const gaugeSeries = computed(() => [estimate.value.percent]);
</script>

<template>
  <ValueAddedCard
    title="保險精算"
    subtitle="以水質監測與衛生據點密度估計營運風險曝險程度。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          水質監測量
        </div>
        <div class="summary-value">
          {{ formatNumber(estimate.waterLoad) }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          支援據點
        </div>
        <div class="summary-value">
          {{ formatNumber(estimate.officeCount, " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          曝險等級
        </div>
        <div class="summary-value">
          {{ estimate.level }}
        </div>
      </div>
    </div>
    <apexchart
      v-if="!loading"
      type="radialBar"
      width="100%"
      height="180"
      :options="gaugeOptions"
      :series="gaugeSeries"
    />
    <p class="note">
      可把「{{ officeTypes[0]?.label || "主要據點" }}」納入理賠與食安事件通報節點，縮短事件後處置時間。
    </p>
  </ValueAddedCard>
</template>
