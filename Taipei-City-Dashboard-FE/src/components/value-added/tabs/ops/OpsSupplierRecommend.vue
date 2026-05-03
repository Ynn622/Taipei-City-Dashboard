<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, sortByDistanceThenDistrict } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.foodSource);
	loading.value = false;
});

const recommended = computed(() => sortByDistanceThenDistrict(rows.value, store.userProfile.userLocation, {
	fallbackDistricts: store.userProfile.focusDistricts,
}).slice(0, 8));
</script>

<template>
  <ValueAddedCard
    title="安全供應來源推薦"
    subtitle="依目前位置與行政區距離排序，優先推薦較近的可替代供應來源。"
    :loading="loading"
  >
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
      未提供精準座標時，會以輪廓所在地行政區中心點作為距離排序基準。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
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
