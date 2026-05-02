<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, sumRows, topRows, trendSummary } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const violationRows = ref([]);
const infectiousRows = ref([]);
const waterRows = ref([]);

onMounted(async () => {
	const [violations, infectious, water] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.infectious),
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
	]);
	violationRows.value = violations;
	infectiousRows.value = infectious;
	waterRows.value = water;
	loading.value = false;
});

const hotspot = computed(() => topRows(violationRows.value, 1)[0]);
const trend = computed(() => trendSummary(infectiousRows.value));
const score = computed(() => {
	const base = 100;
	const trendDelta = trend.value.delta === null ? 0 : Math.max(trend.value.delta, 0);
	const penalty = Math.min((hotspot.value?.value || 0) * 0.8 + trendDelta / 100, 55);
	return Math.round(base - penalty);
});

const gaugeColor = computed(() => {
	if (score.value >= 70) return ["#30B68F"];
	if (score.value >= 50) return ["#F5B041"];
	return ["#D84C73"];
});

const gaugeOptions = computed(() => ({
	chart: { type: "radialBar", background: "transparent", fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: gaugeColor.value,
	plotOptions: {
		radialBar: {
			hollow: { size: "55%" },
			track: { background: "#494b4e" },
			dataLabels: {
				name: { show: true, fontSize: "13px", color: "#888787", offsetY: -8 },
				value: {
					show: true,
					fontSize: "2rem",
					fontWeight: 800,
					color: "#fff",
					offsetY: 4,
					formatter: () => String(score.value),
				},
			},
		},
	},
	labels: ["安全分數"],
}));
</script>

<template>
  <ValueAddedCard
    title="餐廳食安評估"
    subtitle="用違規熱點、腹瀉趨勢與水質資料估算一般外食風險。"
    :loading="loading"
  >
    <apexchart
      v-if="!loading"
      type="radialBar"
      width="100%"
      height="200"
      :options="gaugeOptions"
      :series="[score]"
    />
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          違規熱點
        </div>
        <div class="summary-value">
          {{ hotspot?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          水質監測
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(waterRows)) }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          就診趨勢
        </div>
        <div class="summary-value">
          {{ trend.direction || "無資料" }}
        </div>
      </div>
    </div>
  </ValueAddedCard>
</template>
