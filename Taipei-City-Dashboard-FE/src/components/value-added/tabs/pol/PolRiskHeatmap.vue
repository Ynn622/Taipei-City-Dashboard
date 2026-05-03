<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import ValueAddedMapPanel from "../../ValueAddedMapPanel.vue";
import {
	COMPONENT_IDS,
	districtLocation,
	filterRowsByDateRange,
	formatNumber,
	parseMetricDate,
	rankRows,
	sortByDistanceThenDistrict,
	trendSummary,
	unwrapRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const initialDateRange = parseDateRange(store.userProfile.dateRangeText || "");
const startDate = ref("");
const endDate = ref("");
const startIndex = ref(0);
const endIndex = ref(0);
const areaLevel = ref("district");
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
	initializeDateRange();
	loading.value = false;
});

watch(areaLevel, () => {
	selected.value = null;
});

watch([startIndex, endIndex], () => {
	const range = sortedDateIndices.value;
	startDate.value = dateOptions.value[range.start] || "";
	endDate.value = dateOptions.value[range.end] || "";
	selected.value = null;
});

const dateRangeText = computed(() => {
	if (!startDate.value || !endDate.value) return "";
	return `${compactDate(startDate.value)}-${compactDate(endDate.value)}`;
});
const actualDateOptions = computed(() => getMetricDateOptions(auditRows.value));
const hasActualDateOptions = computed(() => actualDateOptions.value.length >= 2);
const dateOptions = computed(() => hasActualDateOptions.value ? actualDateOptions.value : fallbackDateOptions());
const dateSliderMax = computed(() => Math.max(dateOptions.value.length - 1, 0));
const sortedDateIndices = computed(() => ({
	start: Math.min(startIndex.value, endIndex.value),
	end: Math.max(startIndex.value, endIndex.value),
}));
const dateRangeLabel = computed(() => {
	if (!startDate.value || !endDate.value) return "全部日期";
	return `${startDate.value} - ${endDate.value}`;
});
const filteredAuditRows = computed(() => filterRowsByDateRange(auditRows.value, dateRangeText.value));
const districtRisks = computed(() => rankRows(filteredAuditRows.value, { limit: 99 }));
const cityRisks = computed(() => aggregateDistrictsByCity(districtRisks.value));
const activeRisks = computed(() => areaLevel.value === "city" ? cityRisks.value : districtRisks.value);
const hotspots = computed(() => activeRisks.value.slice(0, 8));
const selectedArea = computed(() => selected.value || hotspots.value[0]);
const selectedLocation = computed(() => districtLocation(selectedArea.value?.label));
const nearestWaterFactor = computed(() => {
	if (!selectedLocation.value) return rankRows(waterRows.value, { limit: 1 })[0] || null;
	return sortByDistanceThenDistrict(waterRows.value, selectedLocation.value)[0] || null;
});
const humanTrend = computed(() => trendSummary(infectiousRows.value));
const waterFactorText = computed(() => {
	if (!selectedArea.value) return "請先選取地區";
	if (!nearestWaterFactor.value) return "附近檢測站資料待補";
	return `${nearestWaterFactor.value.label} ${nearestWaterFactor.value.distanceText}，水質指標 ${formatNumber(nearestWaterFactor.value.value)}`;
});
const humanImpactText = computed(() => {
	if (!selectedArea.value) return "請先選取地區";
	if (!humanTrend.value.hasData) {
		return `違規 ${formatNumber(selectedArea.value.value, " 件")}，腹瀉就診趨勢待補`;
	}
	const trendText = humanTrend.value.delta === null
		? humanTrend.value.direction
		: `${humanTrend.value.direction} ${formatNumber(Math.abs(humanTrend.value.delta), " 人次")}`;
	return `違規 ${formatNumber(selectedArea.value.value, " 件")}，近期腹瀉就診 ${formatNumber(humanTrend.value.latest, " 人次")}（${trendText}）`;
});
const mapDistricts = computed(() => {
	const maxValue = Math.max(...activeRisks.value.map((item) => item.value), 1);
	return activeRisks.value.map((item) => {
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

function initializeDateRange() {
	const options = dateOptions.value;
	if (options.length === 0) return;
	const initialStart = initialDateRange.start && options.includes(initialDateRange.start)
		? initialDateRange.start
		: options[0];
	const initialEnd = initialDateRange.end && options.includes(initialDateRange.end)
		? initialDateRange.end
		: options[options.length - 1];
	startIndex.value = options.indexOf(initialStart);
	endIndex.value = options.indexOf(initialEnd);
	startDate.value = options[sortedDateIndices.value.start] || initialStart;
	endDate.value = options[sortedDateIndices.value.end] || initialEnd;
}

function fallbackDateOptions() {
	const today = new Date();
	return Array.from({ length: 31 }, (_, index) => {
		const date = new Date(today);
		date.setDate(today.getDate() - (30 - index));
		return formatDateInput(date);
	});
}

function getMetricDateOptions(rows) {
	return [...new Set(
		unwrapRows(rows)
			.map((row) => parseMetricDate(row))
			.filter(Boolean)
			.map((date) => formatDateInput(date)),
	)].sort();
}

function aggregateDistrictsByCity(rows) {
	const totals = new Map();
	rows.forEach((item) => {
		const city = cityByDistrict(item.label);
		const current = totals.get(city) || 0;
		totals.set(city, current + item.value);
	});
	return [...totals.entries()]
		.map(([label, value]) => ({ label, value }))
		.sort((a, b) => b.value - a.value)
		.map((item, index) => ({ ...item, rank: index + 1 }));
}

function cityByDistrict(district) {
	if (TAIPEI_DISTRICTS.has(district)) return "臺北市";
	return "新北市";
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

function formatDateInput(date) {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, "0");
	const day = String(date.getDate()).padStart(2, "0");
	return `${year}-${month}-${day}`;
}

const TAIPEI_DISTRICTS = new Set([
	"中正區",
	"大同區",
	"中山區",
	"松山區",
	"大安區",
	"萬華區",
	"信義區",
	"士林區",
	"北投區",
	"內湖區",
	"南港區",
	"文山區",
]);
</script>

<template>
  <ValueAddedCard
    title="食安風險熱區"
    subtitle="用日期區間檢視行政區風險熱點，點選行政區後查看水質因子與人的影響。"
    :loading="loading"
  >
    <template #action>
      <div class="risk-actions">
        <div class="segmented-control">
          <button
            type="button"
            :class="{ active: areaLevel === 'city' }"
            @click="areaLevel = 'city'"
          >
            縣市
          </button>
          <button
            type="button"
            :class="{ active: areaLevel === 'district' }"
            @click="areaLevel = 'district'"
          >
            行政區
          </button>
        </div>
      </div>
    </template>
    <div class="date-range-bar">
      <div class="range-head">
        <span>日期區間</span>
        <strong>{{ dateRangeLabel }}</strong>
      </div>
      <small v-if="!hasActualDateOptions">
        目前資料沒有日期欄位，區間僅調整顯示範圍標籤，地圖套用全部資料。
      </small>
      <div class="dual-range">
        <input
          v-model.number="startIndex"
          type="range"
          min="0"
          :max="dateSliderMax"
        >
        <input
          v-model.number="endIndex"
          type="range"
          min="0"
          :max="dateSliderMax"
        >
      </div>
    </div>
    <ValueAddedMapPanel
      :districts="mapDistricts"
      :area-level="areaLevel"
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
.risk-actions {
  display: flex;
  justify-content: flex-end;
}

.segmented-control {
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(58px, 1fr));
  overflow: hidden;
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.05);

  button {
    min-height: 32px;
    border: 0;
    background: transparent;
    color: var(--color-complement-text);
    font-weight: 700;
    cursor: pointer;
    padding: 0 0.58rem;

    &.active {
      background: var(--color-highlight);
      color: #fff;
    }
  }
}

.date-range-bar {
  display: grid;
  gap: 0.5rem;
  padding: 0.7rem 0.78rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.045);

  .range-head {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    align-items: center;
    font-size: 0.72rem;

    span {
      color: var(--color-complement-text);
    }

    strong {
      color: var(--color-normal-text);
      font-size: 0.8rem;
      text-align: right;
    }
  }

  .dual-range {
    position: relative;
    min-height: 28px;

    input {
      position: absolute;
      inset: 0;
      width: 100%;
      margin: 0;
      background: transparent;
      pointer-events: none;
      accent-color: var(--color-highlight);
    }

    input::-webkit-slider-thumb {
      pointer-events: auto;
      cursor: pointer;
    }

    input::-moz-range-thumb {
      pointer-events: auto;
      cursor: pointer;
    }
  }

  small {
    color: var(--color-complement-text);
    font-size: 0.72rem;
    line-height: 1.45;
  }
}

@media (max-width: 560px) {
  .risk-actions {
    justify-content: flex-start;
  }
}
</style>
