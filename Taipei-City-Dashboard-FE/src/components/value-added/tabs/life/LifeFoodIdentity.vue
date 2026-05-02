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
const sourceRows = ref([]);
const marketRows = ref([]);

onMounted(async () => {
	const [source, market] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.foodSource),
		store.fetchComponentData(COMPONENT_IDS.market),
	]);
	sourceRows.value = source;
	marketRows.value = market;
	loading.value = false;
});

const sourceTop = computed(() => topRows(sourceRows.value, 3));
const marketTop = computed(() => topRows(marketRows.value, 3));
</script>

<template>
  <ValueAddedCard
    title="食物身分證"
    subtitle="用來源農場與市場分布，追溯食材可能的供應節點。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          農場來源
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(sourceRows), " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          市場攤位
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(marketRows), " 攤") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          主要來源
        </div>
        <div class="summary-value">
          {{ sourceTop[0]?.label || "無資料" }}
        </div>
      </div>
    </div>
    <p class="note">
      可從「{{ sourceTop[0]?.label || "農場來源" }}」與「{{ marketTop[0]?.label || "市場節點" }}」交叉追蹤產地、批號與銷售節點。
    </p>
  </ValueAddedCard>
</template>
