<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import ValueAddedMapPanel from "../../ValueAddedMapPanel.vue";
import {
	DISTRICT_COORDS,
	GEOJSON_FILES,
	districtLocation,
	formatNumber,
	rowLabel,
	rowLatLng,
	rowValue,
	unwrapRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const marketRows = ref([]);
const logisticsRows = ref([]);
const waterRows = ref([]);
const selectedDistrict = ref("全部");
const layerOn = ref({
	logistics: true,
	market: true,
	water: true,
});
const radiusUnits = ref({
	logistics: 10,
	market: 20,
	water: 30,
});
const RADIUS_UNIT_METERS = 200;

onMounted(async () => {
	const [market, logistics, water] = await Promise.all([
		fetchRowsFromGeoJson(GEOJSON_FILES.market),
		fetchRowsFromGeoJson(GEOJSON_FILES.logisticsVendor),
		fetchRowsFromGeoJson(GEOJSON_FILES.waterQuality),
	]);
	marketRows.value = market;
	logisticsRows.value = logistics;
	waterRows.value = water;
	loading.value = false;
});

const districtOptions = computed(() => Object.keys(DISTRICT_COORDS));
const filteredMarketRows = computed(() => filterRowsByDistrict(marketRows.value, selectedDistrict.value));
const filteredLogisticsRows = computed(() => filterRowsByDistrict(logisticsRows.value, selectedDistrict.value));
const filteredWaterRows = computed(() => filterRowsByDistrict(waterRows.value, selectedDistrict.value));
const displayMarketRows = computed(() => rowsForMap(filteredMarketRows.value, marketRows.value));
const displayLogisticsRows = computed(() => rowsForMap(filteredLogisticsRows.value, logisticsRows.value));
const displayWaterRows = computed(() => rowsForMap(filteredWaterRows.value, waterRows.value));
const mapPoints = computed(() => [
	...(layerOn.value.market ? displayMarketRows.value.map((row) => pointFromRow(row, "市場", "#E86F51", 10)) : []),
	...(layerOn.value.logistics ? displayLogisticsRows.value.map((row) => pointFromRow(row, "物流", "#30B68F", 9)) : []),
	...(layerOn.value.water ? displayWaterRows.value.map((row) => pointFromRow(row, "水源", "#1E88E5", 9)) : []),
].filter(Boolean));
const mapCircles = computed(() => [
	...(layerOn.value.logistics ? displayLogisticsRows.value.map((row) => circleFromRow(row, "物流", radiusKm("logistics"), "#30B68F", 0.13)) : []),
	...(layerOn.value.market ? displayMarketRows.value.map((row) => circleFromRow(row, "市場", radiusKm("market"), "#E86F51", 0.11)) : []),
	...(layerOn.value.water ? displayWaterRows.value.map((row) => circleFromRow(row, "水源", radiusKm("water"), "#1E88E5", 0.10)) : []),
].filter(Boolean));
const visibleMarketRows = computed(() => layerOn.value.market ? filteredMarketRows.value : []);
const visibleLogisticsRows = computed(() => layerOn.value.logistics ? filteredLogisticsRows.value : []);
const visibleWaterRows = computed(() => layerOn.value.water ? filteredWaterRows.value : []);

async function fetchRowsFromGeoJson(files) {
	const collections = await store.fetchGeoJsonFiles(files);
	return collections.flatMap((collection) => collection.features || [])
		.map((feature) => ({
			...(feature.properties || {}),
			_geometry: feature.geometry,
		}));
}

function rowsForMap(filteredRows, allRows) {
	if (selectedDistrict.value !== "全部") return filteredRows;
	return unwrapRows(allRows).slice(0, 80);
}

function pointFromRow(row, category, color, baseRadius) {
	const location = rowLatLng(row) || districtLocation(row?.district || rowLabel(row));
	if (!location) return null;
	return {
		...location,
		label: `${category} ${row?.name || row?.title || rowLabel(row)}`,
		value: rowValue(row) || 1,
		radius: baseRadius,
		color,
	};
}

function circleFromRow(row, category, radiusKm, color, opacity) {
	const location = rowLatLng(row) || districtLocation(row?.district || rowLabel(row));
	if (!location) return null;
	return {
		...location,
		label: `${category} ${row?.name || row?.title || rowLabel(row)}`,
		radiusKm,
		color,
		opacity,
	};
}

function radiusKm(key) {
	return radiusUnits.value[key] * RADIUS_UNIT_METERS / 1000;
}

function radiusLabel(key) {
	const meters = radiusUnits.value[key] * RADIUS_UNIT_METERS;
	if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
	return `${meters} m`;
}

function filterRowsByDistrict(rows, district) {
	if (!district || district === "全部") return unwrapRows(rows);
	return unwrapRows(rows).filter((row) => row?.district === district || rowLabel(row) === district);
}
</script>

<template>
  <ValueAddedCard
    title="食安事件範圍推斷"
    subtitle="可調整物流、市場與水源半徑，渲染可能影響範圍。"
    :loading="loading"
  >
    <template #action>
      <select
        v-model="selectedDistrict"
        class="district-select"
      >
        <option value="全部">
          全部行政區
        </option>
        <option
          v-for="district in districtOptions"
          :key="district"
          :value="district"
        >
          {{ district }}
        </option>
      </select>
    </template>
    <div class="radius-controls">
      <label>
        <input
          v-model="layerOn.logistics"
          type="checkbox"
        >
        <span>物流 {{ radiusLabel("logistics") }}</span>
        <input
          v-model.number="radiusUnits.logistics"
          type="range"
          min="1"
          max="30"
          step="1"
          :disabled="!layerOn.logistics"
        >
      </label>
      <label>
        <input
          v-model="layerOn.market"
          type="checkbox"
        >
        <span>市場 {{ radiusLabel("market") }}</span>
        <input
          v-model.number="radiusUnits.market"
          type="range"
          min="1"
          max="30"
          step="1"
          :disabled="!layerOn.market"
        >
      </label>
      <label>
        <input
          v-model="layerOn.water"
          type="checkbox"
        >
        <span>水源 {{ radiusLabel("water") }}</span>
        <input
          v-model.number="radiusUnits.water"
          type="range"
          min="1"
          max="30"
          step="1"
          :disabled="!layerOn.water"
        >
      </label>
    </div>
    <ValueAddedMapPanel
      :points="mapPoints"
      :circles="mapCircles"
      :height="235"
    />
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          市場節點
        </div>
        <div class="summary-value">
          {{ formatNumber(visibleMarketRows.length, " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          物流節點
        </div>
        <div class="summary-value">
          {{ formatNumber(visibleLogisticsRows.length, " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          水質監測
        </div>
        <div class="summary-value">
          {{ formatNumber(visibleWaterRows.length, " 站") }}
        </div>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.district-select {
  min-height: 32px;
  min-width: 116px;
  border: solid 1px var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-normal-text);
  padding: 0.28rem 0.5rem;
  font-size: 0.82rem;
}

.radius-controls {
  display: grid;
  gap: 0.5rem;
  color: var(--color-complement-text);
  font-size: 0.78rem;

  label {
    display: grid;
    grid-template-columns: auto 104px minmax(0, 1fr);
    gap: 0.6rem;
    align-items: center;
  }

  input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--color-highlight);
  }

  input[type="range"]:disabled {
    opacity: 0.35;
  }
}

</style>
