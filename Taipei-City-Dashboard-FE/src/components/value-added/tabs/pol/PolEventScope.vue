<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import ValueAddedMapPanel from "../../ValueAddedMapPanel.vue";
import { COMPONENT_IDS, districtLocation, formatNumber, normalizeLatLng, sumRows, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const marketRows = ref([]);
const waterRows = ref([]);
const radius = ref({
	logistics: 2,
	market: 4,
	water: 6,
});

onMounted(async () => {
	const [market, water] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.market),
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
	]);
	marketRows.value = market;
	waterRows.value = water;
	loading.value = false;
});

const marketHotspots = computed(() => topRows(marketRows.value, 3));
const waterHotspots = computed(() => topRows(waterRows.value, 3));
const mapCenter = computed(() => {
	const profileLocation = normalizeLatLng(store.userProfile.userLocation);
	if (profileLocation) return profileLocation;
	return districtLocation(marketHotspots.value[0]?.label) || districtLocation(waterHotspots.value[0]?.label) || { lat: 25.0448, lng: 121.5366 };
});
const mapPoints = computed(() => [
	...marketHotspots.value.map((item) => pointFromDistrict(item, "#E86F51", 12)),
	...waterHotspots.value.map((item) => pointFromDistrict(item, "#1E88E5", 10)),
	{
		...mapCenter.value,
		label: "推估中心",
		value: 0,
		radius: 8,
		color: "#F2C94C",
	},
].filter(Boolean));
const mapCircles = computed(() => [
	{
		...mapCenter.value,
		label: "物流",
		radiusKm: radius.value.logistics,
		color: "#30B68F",
		opacity: 0.18,
	},
	{
		...mapCenter.value,
		label: "市場",
		radiusKm: radius.value.market,
		color: "#E86F51",
		opacity: 0.14,
	},
	{
		...mapCenter.value,
		label: "水源",
		radiusKm: radius.value.water,
		color: "#1E88E5",
		opacity: 0.12,
	},
]);

function pointFromDistrict(item, color, baseRadius) {
	const location = districtLocation(item.label);
	if (!location) return null;
	return {
		...location,
		label: item.label,
		value: item.value,
		radius: baseRadius,
		color,
	};
}
</script>

<template>
  <ValueAddedCard
    title="食安事件範圍推斷"
    subtitle="可調整物流、市場與水源半徑，渲染可能影響範圍。"
    :loading="loading"
  >
    <div class="radius-controls">
      <label>物流 {{ radius.logistics }} km <input
        v-model.number="radius.logistics"
        type="range"
        min="1"
        max="12"
      ></label>
      <label>市場 {{ radius.market }} km <input
        v-model.number="radius.market"
        type="range"
        min="1"
        max="12"
      ></label>
      <label>水源 {{ radius.water }} km <input
        v-model.number="radius.water"
        type="range"
        min="1"
        max="12"
      ></label>
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
          {{ formatNumber(sumRows(marketRows), " 攤") }}
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
          優先範圍
        </div>
        <div class="summary-value">
          {{ marketHotspots[0]?.label || waterHotspots[0]?.label || "無資料" }}
        </div>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.radius-controls {
  display: grid;
  gap: 0.5rem;
  color: var(--color-complement-text);
  font-size: 0.78rem;

  label {
    display: grid;
    grid-template-columns: 82px minmax(0, 1fr);
    gap: 0.6rem;
    align-items: center;
  }
}

</style>
