<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	sumRows,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const marketRows = ref([]);
const waterRows = ref([]);

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
</script>

<template>
  <ValueAddedCard
    title="食安事件範圍推斷"
    subtitle="從市場與水源節點推估事件可能擴散範圍。"
    :loading="loading"
  >
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
    <p class="note">
      若市場熱點與水源熱點重疊，建議把該行政區列為第一波採樣與公告範圍。
    </p>
  </ValueAddedCard>
</template>
