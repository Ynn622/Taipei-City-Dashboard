<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, formatNumber, rankRows, sumRows, topRows, trendSummary } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const query = ref("");
const selectedBranch = ref(null);
const violationRows = ref([]);
const infectiousRows = ref([]);
const waterRows = ref([]);
const restaurantRows = ref([]);

onMounted(async () => {
	const [violations, infectious, water, restaurants] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.infectious),
		store.fetchComponentData(COMPONENT_IDS.waterQuality),
		store.fetchComponentData(COMPONENT_IDS.goodRestaurants),
	]);
	violationRows.value = violations;
	infectiousRows.value = infectious;
	waterRows.value = water;
	restaurantRows.value = restaurants;
	loading.value = false;
});

const candidates = computed(() => {
	const keyword = query.value.trim();
	const rows = rankRows(restaurantRows.value, { limit: 12 });
	if (!keyword) return rows.slice(0, 5);
	return rows.filter((item) => item.label.includes(keyword)).slice(0, 6);
});
const target = computed(() => selectedBranch.value || candidates.value[0]);
const hotspot = computed(() => topRows(violationRows.value, 1)[0]);
const trend = computed(() => trendSummary(infectiousRows.value));
const score = computed(() => {
	const trendDelta = trend.value.delta === null ? 0 : Math.max(trend.value.delta, 0);
	const penalty = Math.min((hotspot.value?.value || 0) * 0.8 + trendDelta / 100, 55);
	return Math.round(100 - penalty);
});
</script>

<template>
  <ValueAddedCard
    title="餐廳食安評估"
    subtitle="輸入餐廳名稱後選擇候選分店，檢視歷史違規、附近水質與短期腹瀉趨勢。"
    :loading="loading"
  >
    <div class="search-row">
      <input
        v-model="query"
        type="text"
        placeholder="輸入餐廳或行政區名稱"
      >
    </div>
    <div class="candidate-list">
      <button
        v-for="item in candidates"
        :key="item.label"
        type="button"
        :class="{ active: target?.label === item.label }"
        @click="selectedBranch = item"
      >
        <span>{{ item.label }}</span>
        <strong>{{ formatNumber(item.value, " 家") }}</strong>
      </button>
    </div>
    <div class="score-panel">
      <strong>{{ score }}</strong>
      <span>{{ target?.label || "候選分店" }} 食安分數</span>
    </div>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          歷史違規熱點
        </div>
        <div class="summary-value">
          {{ hotspot?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          附近水質
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(waterRows)) }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          腹瀉趨勢
        </div>
        <div class="summary-value">
          {{ trend.direction || "無資料" }}
        </div>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.search-row input {
  width: 100%;
  box-sizing: border-box;
  border: solid 1px rgba(255, 255, 255, 0.12);
  border-radius: 7px;
  background: rgba(9, 9, 9, 0.35);
  color: var(--color-normal-text);
  padding: 0.65rem 0.75rem;
}

.candidate-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;

  button {
    display: inline-flex;
    gap: 0.45rem;
    align-items: center;
    border: solid 1px rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.045);
    color: var(--color-normal-text);
    padding: 0.48rem 0.65rem;
    cursor: pointer;

    &.active {
      border-color: rgba(48, 182, 143, 0.8);
      background: rgba(48, 182, 143, 0.14);
    }
  }
}

.score-panel {
  display: grid;
  place-items: center;
  min-height: 148px;
  border-radius: 8px;
  background: rgba(48, 182, 143, 0.11);

  strong {
    color: var(--color-normal-text);
    font-size: 3.6rem;
    line-height: 1;
  }

  span {
    color: var(--color-complement-text);
    font-weight: 800;
  }
}
</style>
