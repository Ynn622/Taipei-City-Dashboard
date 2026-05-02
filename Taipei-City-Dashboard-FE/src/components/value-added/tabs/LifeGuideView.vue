<script setup>
import LifeFoodSpin from "./life/LifeFoodSpin.vue";
import LifeRestaurantSafety from "./life/LifeRestaurantSafety.vue";
import LifeQuickHelp from "./life/LifeQuickHelp.vue";
import LifeFoodIdentity from "./life/LifeFoodIdentity.vue";
</script>
<template>
  <div class="tab-view">
    <div class="tab-column">
      <LifeFoodSpin />
      <LifeQuickHelp />
    </div>
    <div class="tab-column stretch-column">
      <div class="restaurant-safety-slot">
        <LifeRestaurantSafety />
      </div>
      <LifeFoodIdentity />
    </div>
  </div>
</template>

<style scoped lang="scss">
.tab-view {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
}

.tab-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.stretch-column {
  height: 100%;
}

.restaurant-safety-slot {
  display: flex;
  flex: 0 0 auto;
  min-height: 0;

  :deep(.value-card) {
    width: 100%;
  }
}

@media (max-width: 860px) {
  .tab-view {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .restaurant-safety-slot {
    flex: 0 1 auto;

    :deep(.value-card) {
      height: auto;
    }
  }
}
</style>
