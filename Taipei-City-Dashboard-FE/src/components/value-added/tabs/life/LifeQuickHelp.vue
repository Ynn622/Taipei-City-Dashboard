<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, sortByDistanceThenDistrict } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const selectedType = ref("全部");

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.postHelpAgency);
	loading.value = false;
});

const allResources = computed(() => sortByDistanceThenDistrict(rows.value, store.userProfile.userLocation, {
	fallbackDistricts: store.userProfile.focusDistricts,
}));
const types = computed(() => ["全部", ...new Set(allResources.value.map((item) => item.label).filter(Boolean))].slice(0, 8));
const resources = computed(() => allResources.value
	.filter((item) => selectedType.value === "全部" || item.label === selectedType.value)
	.slice(0, 8));
</script>

<template>
  <ValueAddedCard
    title="快速求助"
    subtitle="依目前所在地距離排序醫療與食安事件支援資源。"
    :loading="loading"
  >
    <template #action>
      <select v-model="selectedType">
        <option
          v-for="type in types"
          :key="type"
        >
          {{ type }}
        </option>
      </select>
    </template>
    <div class="resource-list">
      <div
        v-for="item in resources"
        :key="`${item.label}-${item.distanceText}`"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.distanceText }}</strong>
        <small>{{ formatNumber(item.value, " 處") }}</small>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
select {
  border: solid 1px var(--color-border);
  border-radius: 5px;
  background: var(--color-background);
  color: var(--color-normal-text);
  padding: 0.35rem 0.5rem;
}

.resource-list {
  display: grid;
  gap: 0.55rem;

  div {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    gap: 0.6rem;
    align-items: center;
    padding: 0.62rem 0.7rem;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.045);
  }

  span {
    color: var(--color-normal-text);
    font-weight: 800;
  }

  strong {
    color: #72C6A4;
  }

  small {
    color: var(--color-complement-text);
  }
}
</style>
