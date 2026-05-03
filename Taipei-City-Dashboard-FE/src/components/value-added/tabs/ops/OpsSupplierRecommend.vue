<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, sortByDistanceThenDistrict } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const locating = ref(false);
const locationStatus = ref("尚未定位");
const currentLocation = ref(null);
const rows = ref([]);

onMounted(async () => {
	const [source] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.foodSource),
		refreshCurrentLocation(),
	]);
	rows.value = source;
	loading.value = false;
});

const locationForSort = computed(() => currentLocation.value || store.userProfile.userLocation);
const recommended = computed(() => sortByDistanceThenDistrict(rows.value, locationForSort.value, {
	fallbackDistricts: store.userProfile.focusDistricts,
}).slice(0, 8));

async function refreshCurrentLocation() {
	if (!navigator.geolocation) {
		locationStatus.value = "此瀏覽器不支援定位，改用輪廓所在地";
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
				locationStatus.value = store.userProfile.userLocation
					? "定位未允許，改用輪廓位置"
					: "定位未允許，改用輪廓行政區";
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
    title="安全供應來源推薦"
    subtitle="依目前位置與行政區距離排序，優先推薦較近的可替代供應來源。"
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
    <div class="rank-list">
      <div
        v-for="item in recommended"
        :key="item.label"
        class="rank-item"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.distanceText }}</strong>
        <small>{{ formatNumber(item.value, " 處") }}</small>
      </div>
    </div>
    <p class="note">
      若無法取得目前位置，會以輪廓位置或所在地行政區中心點作為距離排序基準。
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

.rank-list {
  display: grid;
  gap: 0.55rem;
}

.rank-item {
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
