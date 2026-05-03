<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import ValueAddedMapPanel from "../../ValueAddedMapPanel.vue";
import {
	COMPONENT_IDS,
	districtLocation,
	filterRowsByDateRange,
	formatNumber,
	rankRows,
	sortByDistanceThenDistrict,
	trendSummary,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const initialDateRange = parseDateRange(store.userProfile.dateRangeText || "");
const startDate = ref(initialDateRange.start);
const endDate = ref(initialDateRange.end);
const selected = ref(null);
const auditRows = ref([]);
const waterRows = ref([]);
const infectiousRows = ref([]);

onMounted(async () => {
	const [audit, water, infectious] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
		store.fetchComponentData(COMPONENT_IDS.infectious),
	]);
	auditRows.value = audit;
	waterRows.value = water;
	infectiousRows.value = infectious;
	loading.value = false;
});

const dateRangeText = computed(() => {
	if (!startDate.value || !endDate.value) return "";
	return `${compactDate(startDate.value)}-${compactDate(endDate.value)}`;
});
const districtRisks = computed(() => rankRows(filterRowsByDateRange(auditRows.value, dateRangeText.value), { limit: 99 }));
const hotspots = computed(() => districtRisks.value.slice(0, 8));
const selectedArea = computed(() => selected.value || hotspots.value[0]);
const selectedLocation = computed(() => districtLocation(selectedArea.value?.label));
const nearestWaterFactor = computed(() => {
	if (!selectedLocation.value) return rankRows(waterRows.value, { limit: 1 })[0] || null;
	return sortByDistanceThenDistrict(waterRows.value, selectedLocation.value)[0] || null;
});
const humanTrend = computed(() => trendSummary(infectiousRows.value));
const waterFactorText = computed(() => {
	if (!selectedArea.value) return "請先選取行政區";
	if (!nearestWaterFactor.value) return "附近檢測站資料待補";
	return `${nearestWaterFactor.value.label} ${nearestWaterFactor.value.distanceText}，水質指標 ${formatNumber(nearestWaterFactor.value.value)}`;
});
const humanImpactText = computed(() => {
	if (!selectedArea.value) return "請先選取行政區";
	if (!humanTrend.value.hasData) {
		return `違規 ${formatNumber(selectedArea.value.value, " 件")}，腹瀉就診趨勢待補`;
	}
	const trendText = humanTrend.value.delta === null
		? humanTrend.value.direction
		: `${humanTrend.value.direction} ${formatNumber(Math.abs(humanTrend.value.delta), " 人次")}`;
	return `違規 ${formatNumber(selectedArea.value.value, " 件")}，近期腹瀉就診 ${formatNumber(humanTrend.value.latest, " 人次")}（${trendText}）`;
});
const mapDistricts = computed(() => {
	const maxValue = Math.max(...districtRisks.value.map((item) => item.value), 1);
	return districtRisks.value.map((item) => {
		const intensity = item.value / maxValue;
		return {
			label: item.label,
			value: item.value,
			color: heatColor(intensity),
			opacity: Math.min(0.84, Math.max(0.14, 0.18 + intensity * 0.62)),
		};
	});
});

function heatColor(intensity) {
	if (intensity >= 0.82) return "#B8325A";
	if (intensity >= 0.62) return "#D84C73";
	if (intensity >= 0.42) return "#E86F51";
	if (intensity >= 0.24) return "#F2C94C";
	return "#72C6A4";
}

function parseDateRange(value) {
	const [start = "", end = ""] = String(value || "").split("-");
	return {
		start: dateInputValue(start),
		end: dateInputValue(end),
	};
}

function dateInputValue(value) {
	const raw = String(value || "").trim();
	const compact = raw.match(/^(\d{4})(\d{2})(\d{2})$/);
	const dashed = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
	const match = compact || dashed;
	if (!match) return "";
	const month = match[2].padStart(2, "0");
	const day = match[3].padStart(2, "0");
	return `${match[1]}-${month}-${day}`;
}

function compactDate(value) {
	return String(value || "").replaceAll("-", "");
}
</script>

<template>
  <ValueAddedCard
    title="食安風險熱區"
    subtitle="用日期區間檢視行政區風險熱點，點選行政區後查看水質因子與人的影響。"
    :loading="loading"
  >
    <template #action>
      <div class="date-controls">
        <label>
          <span>開始</span>
          <input
            v-model="startDate"
            type="date"
          >
        </label>
        <label>
          <span>結束</span>
          <input
            v-model="endDate"
            type="date"
          >
        </label>
      </div>
    </template>
    <ValueAddedMapPanel
      :districts="mapDistricts"
      :selected-label="selectedArea?.label"
      :height="260"
      @select="selected = $event"
    />
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          選取地區
        </div>
        <div class="summary-value">
          {{ selectedArea?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          違規因子(水質)
        </div>
        <div class="summary-value">
          {{ waterFactorText }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          對人的影響
        </div>
        <div class="summary-value">
          {{ humanImpactText }}
        </div>
      </div>
    </div>
    <p class="note">
      違規因子以選取行政區附近水質檢測站作為參照；人的影響以腹瀉就診趨勢與該區違規量共同判讀。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.date-controls {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 0.45rem;

  label {
    display: flex;
    flex-direction: column;
    gap: 0.22rem;
    color: var(--color-complement-text);
    font-size: 0.72rem;
  }

  input {
    min-height: 32px;
    border: solid 1px var(--color-border);
    border-radius: 5px;
    background: var(--color-background);
    color: var(--color-normal-text);
    padding: 0.25rem 0.42rem;
    font-size: 0.78rem;
  }
}

@media (max-width: 560px) {
  .date-controls {
    grid-template-columns: 1fr;
  }
}
</style>
