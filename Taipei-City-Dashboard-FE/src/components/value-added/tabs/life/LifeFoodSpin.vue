<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	profileCategories,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const selectedIndex = ref(0);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.goodRestaurants);
	loading.value = false;
});

const options = computed(() => topRows(rows.value, 6));
const selected = computed(() => options.value[selectedIndex.value % Math.max(options.value.length, 1)]);
const preference = computed(() => profileCategories(store.userProfile).join("、") || "均衡飲食");

function spin() {
	if (options.value.length === 0) return;
	selectedIndex.value = Math.floor(Math.random() * options.value.length);
}
</script>

<template>
  <ValueAddedCard
    title="今天吃什麼？"
    subtitle="結合優良餐廳分布與偏好輪廓，提供一個可執行選項。"
    :loading="loading"
  >
    <template #action>
      <button
        class="action-btn"
        @click="spin"
      >
        轉一下
      </button>
    </template>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          推薦區域
        </div>
        <div class="summary-value">
          {{ selected?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          優良餐廳量
        </div>
        <div class="summary-value">
          {{ formatNumber(selected?.value || 0, " 家") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          偏好
        </div>
        <div class="summary-value">
          {{ preference }}
        </div>
      </div>
    </div>
    <p class="note">
      先選高覆蓋的優良餐廳行政區，再避開近期違規熱點會更穩。
    </p>
  </ValueAddedCard>
</template>
