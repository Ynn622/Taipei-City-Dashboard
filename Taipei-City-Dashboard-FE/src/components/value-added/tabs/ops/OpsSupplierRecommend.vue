<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import ValueAddedMapPanel from "../../ValueAddedMapPanel.vue";
import {
	GEOJSON_FILES,
	districtLocation,
	rowLabel,
	rowLatLng,
	sortByDistanceThenDistrict,
} from "../../valueAddedAnalytics";

const DEFAULT_ORIGIN = { lat: 25.044808, lng: 121.536609 };
const ORGANIC_FARM_KEYWORD = "有機";
const store = useValueAddedStore();
const loading = ref(true);
const locating = ref(false);
const locationStatus = ref("尚未定位");
const currentLocation = ref(null);
const rows = ref([]);

onMounted(async () => {
	const [sourceRows] = await Promise.all([
		fetchSourceRows(),
		refreshCurrentLocation(),
	]);
	rows.value = sourceRows;
	loading.value = false;
});

const locationForSort = computed(() => (
	currentLocation.value ||
	store.userProfile.userLocation ||
	districtLocation(store.userProfile.focusDistricts?.[0]) ||
	DEFAULT_ORIGIN
));
const recommended = computed(() => sortByDistanceThenDistrict(rows.value, locationForSort.value, {
	fallbackDistricts: store.userProfile.focusDistricts,
}).slice(0, 6));
const originPoint = computed(() => {
	const location = locationForSort.value;
	if (!location) return null;
	return {
		...location,
		label: "目前位置",
		value: 1,
		radius: 11,
		color: "#4A90E2",
	};
});
const supplierPoints = computed(() => recommended.value
	.map((item) => {
		const location = rowLatLng(item.row);
		if (!location) return null;
		return {
			...location,
			label: item.label,
			value: Number(item.row?.area_ha || item.value || 1),
			radius: 9,
			color: "#72C6A4",
		};
	})
	.filter(Boolean));
const mapPoints = computed(() => [
	...(originPoint.value ? [originPoint.value] : []),
	...supplierPoints.value,
]);
const mapLines = computed(() => {
	const origin = originPoint.value;
	if (!origin) return [];
	return recommended.value
		.map((item, index) => {
			const target = rowLatLng(item.row);
			if (!target) return null;
			return {
				from: origin,
				to: target,
				label: item.label,
				value: item.distance || 0,
				color: index === 0 ? "#F2C94C" : "#72C6A4",
				opacity: index === 0 ? 0.95 : 0.58,
				width: index === 0 ? 3.2 : 2,
			};
		})
		.filter(Boolean);
});

async function fetchSourceRows() {
	const collections = await store.fetchGeoJsonFiles(GEOJSON_FILES.foodSource);
	return collections.flatMap((collection) => collection.features || [])
		.map((feature) => normalizeOrganicFarmRow(feature))
		.filter(Boolean);
}

function supplierAreaText(item) {
	const area = Number(item.row?.area_ha);
	if (!Number.isFinite(area) || area <= 0) return rowLabel(item.row);
	return `${formatArea(area)} ha`;
}

function isOrganicFarm(row) {
	const isOrganicFarmSource = (
		String(row?.source_type || "").includes("有機農場") ||
		String(row?.source_dataset || "").includes("有機農場")
	);
	return (
		isOrganicFarmSource &&
		String(row?.certification_status || "").includes(ORGANIC_FARM_KEYWORD)
	);
}

function normalizeOrganicFarmRow(feature) {
	const row = {
		...(feature.properties || {}),
		_geometry: feature.geometry,
	};
	const farmName = organicFarmName(row);
	if (!isOrganicFarm(row) || !farmName) return null;
	return {
		...row,
		x_axis: farmName,
	};
}

function organicFarmName(row) {
	const name = String(row?.name || "").trim();
	const bracketName = name.match(/[（(]([^()（）]+)[）)]/);
	if (bracketName?.[1]) return bracketName[1].trim();
	if (hasOrganizationLikeName(name)) return name;
	return "";
}

function hasOrganizationLikeName(name) {
	return /公司|農場|農園|茶園|農莊|園圃|合作社|產銷班|休閒農場|茶坊|農舍|農業/.test(name);
}

function formatArea(area) {
	if (area >= 10) return area.toFixed(1);
	if (area >= 1) return area.toFixed(2);
	return area.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

async function refreshCurrentLocation() {
	if (!navigator.geolocation) {
		locationStatus.value = store.userProfile.userLocation || store.userProfile.focusDistricts?.length
			? "此瀏覽器不支援定位，改用輪廓所在地"
			: "此瀏覽器不支援定位，改用臺北市中心點";
		return null;
	}
	locating.value = true;
	locationStatus.value = "正在取得目前位置...";
	return new Promise((resolve) => {
		navigator.geolocation.getCurrentPosition(
			(position) => {
				const location = {
					lat: Number(position.coords.latitude.toFixed(6)),
					lng: Number(position.coords.longitude.toFixed(6)),
				};
				currentLocation.value = location;
				store.saveProfile({ userLocation: location });
				locationStatus.value = "已使用目前位置排序";
				locating.value = false;
				resolve(location);
			},
			() => {
				if (store.userProfile.userLocation) {
					locationStatus.value = "定位未允許，改用輪廓位置";
				} else if (store.userProfile.focusDistricts?.length) {
					locationStatus.value = "定位未允許，改用輪廓行政區";
				} else {
					locationStatus.value = "定位未允許，改用臺北市中心點";
				}
				locating.value = false;
				resolve(null);
			},
			{
				enableHighAccuracy: true,
				timeout: 8000,
				maximumAge: 60000,
			}
		);
	});
}
</script>

<template>
  <ValueAddedCard
    class="supplier-card"
    title="安全供應來源推薦"
    subtitle="以地圖線層連接目前位置與較近的有機農場。"
    :loading="loading"
  >
    <template #action>
      <button
        type="button"
        class="locate-btn"
        :disabled="locating"
        @click="refreshCurrentLocation"
      >
        <span>my_location</span>
        {{ locating ? "定位中" : "重新定位" }}
      </button>
    </template>
    <div class="location-state">
      {{ locationStatus }}
    </div>
    <ValueAddedMapPanel
      class="supplier-map"
      :points="mapPoints"
      :lines="mapLines"
      :height="260"
    />
    <div class="route-list">
      <div
        v-for="item in recommended"
        :key="item.label"
        class="route-item"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.distanceText }}</strong>
        <small>{{ supplierAreaText(item) }}</small>
      </div>
    </div>
    <p class="note">
      線段由目前位置或輪廓行政區中心點連到有機農場點位，黃色線代表最近推薦。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.locate-btn {
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);
  font-weight: 700;
  padding: 0.34rem 0.62rem;
  cursor: pointer;

  span {
    font-family: var(--font-icon);
    font-size: 1rem;
  }

  &:disabled {
    cursor: wait;
    opacity: 0.62;
  }
}

.location-state {
  color: var(--color-complement-text);
  font-size: 0.8rem;
  line-height: 1.5;
  padding: 0.48rem 0.62rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.045);
}

.supplier-map {
  flex: 1 1 260px;
  min-height: 260px;
}

:deep(.supplier-card .card-body) {
  min-height: 0;
}

.route-list {
  display: grid;
  gap: 0.55rem;
}

.route-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 0.6rem;
  align-items: center;
  padding: 0.62rem 0.7rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.045);

  span,
  strong,
  small {
    min-width: 0;
  }

  span {
    color: var(--color-normal-text);
    font-weight: 700;
  }

  strong {
    color: #72C6A4;
  }

  small {
    color: var(--color-complement-text);
  }
}
</style>
