<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	computePeriodDelta,
	filterByProfileDistrict,
	formatNumber,
	rowLabel,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const healthRows = ref([]);
const foodRows = ref([]);

onMounted(async () => {
	const [health, food] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.foodAuditViolation),
	]);
	healthRows.value = health;
	foodRows.value = food;
	loading.value = false;
});

const scopedRows = computed(() => [
	...filterByProfileDistrict(healthRows.value, store.userProfile),
	...filterByProfileDistrict(foodRows.value, store.userProfile),
]);
const risks = computed(() => computePeriodDelta(scopedRows.value, {
	groupKey: "business_category",
	limit: 6,
}));
const topDistrict = computed(() => {
	const totals = new Map();
	scopedRows.value.forEach((row) => {
		const label = row?.district || rowLabel(row);
		totals.set(label, (totals.get(label) || 0) + Number(row?.value ?? row?.y ?? row?.data ?? 1));
	});
	return [...totals.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || "無資料";
});
</script>

<template>
  <ValueAddedCard
    title="稽查風險預測"
    subtitle="依同屬性餐廳近期稽查次數排序，輔以最高風險區判斷。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          同屬性最高
        </div>
        <div class="summary-value">
          {{ risks[0]?.label || "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          最高風險區
        </div>
        <div class="summary-value">
          {{ topDistrict }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          近期增幅
        </div>
        <div class="summary-value">
          {{ risks[0] ? formatNumber(risks[0].delta, " 件") : "無資料" }}
        </div>
      </div>
    </div>
    <div class="rank-list">
      <div
        v-for="item in risks"
        :key="item.label"
        class="rank-row"
      >
        <span>#{{ item.rank }} {{ item.label }}</span>
        <strong>{{ formatNumber(item.current, " 件") }}</strong>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.rank-list {
  display: grid;
  gap: 0.45rem;
  margin-top: 0.75rem;
}

.rank-row {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  padding: 0.55rem 0.65rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.045);

  span {
    color: var(--color-normal-text);
    font-weight: 700;
  }

  strong {
    color: #F2C94C;
  }
}
</style>
