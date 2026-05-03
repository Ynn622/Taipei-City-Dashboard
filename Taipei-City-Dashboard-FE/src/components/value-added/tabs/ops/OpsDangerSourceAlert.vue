<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, computePeriodDelta, formatNumber } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.foodAuditViolation);
	loading.value = false;
});

const dangerSources = computed(() => computePeriodDelta(rows.value, {
	groupKey: "product_category",
	limit: 6,
}));
</script>

<template>
  <ValueAddedCard
    title="危險來源迴避"
    subtitle="以近 30 天相較前 30 天的食品類別違規增幅排序。"
    :loading="loading"
  >
    <div class="avoid-list">
      <div
        v-for="item in dangerSources"
        :key="item.label"
        class="avoid-item"
      >
        <div>
          <span>#{{ item.rank }} {{ item.label }}</span>
          <small>近 30 天 {{ formatNumber(item.current, " 件") }} / 前期 {{ formatNumber(item.previous, " 件") }}</small>
        </div>
        <strong>{{ item.delta >= 0 ? "+" : "" }}{{ formatNumber(item.delta, " 件") }}</strong>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.avoid-list {
  display: grid;
  gap: 0.58rem;
}

.avoid-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.7rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.045);

  span {
    display: block;
    color: var(--color-normal-text);
    font-weight: 800;
  }

  small {
    color: var(--color-complement-text);
  }

  strong {
    color: #E86F51;
    font-size: 1.05rem;
  }
}
</style>
