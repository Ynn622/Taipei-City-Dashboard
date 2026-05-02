<script setup>
import LifeFoodSpin from "./life/LifeFoodSpin.vue";
import LifeRestaurantSafety from "./life/LifeRestaurantSafety.vue";
import LifeQuickHelp from "./life/LifeQuickHelp.vue";
import LifeFoodIdentity from "./life/LifeFoodIdentity.vue";
</script>
<template>
  <div class="tab-view">
    <LifeFoodSpin />
    <LifeRestaurantSafety />
    <LifeQuickHelp />
    <LifeFoodIdentity />
  </div>
</template>

<style scoped lang="scss">
.tab-view {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  align-items: start;
}

@media (max-width: 860px) {
  .tab-view {
    grid-template-columns: 1fr;
  }
}
</style>
