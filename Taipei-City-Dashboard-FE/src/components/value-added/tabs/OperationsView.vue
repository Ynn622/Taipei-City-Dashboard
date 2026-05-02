<script setup>
import OpsSupplierRecommend from "./ops/OpsSupplierRecommend.vue";
import OpsDangerSourceAlert from "./ops/OpsDangerSourceAlert.vue";
import OpsAuditRiskPrediction from "./ops/OpsAuditRiskPrediction.vue";
import OpsInsuranceEstimate from "./ops/OpsInsuranceEstimate.vue";
import OpsImproveSuggestion from "./ops/OpsImproveSuggestion.vue";
</script>
<template>
  <div class="tab-view">
    <OpsSupplierRecommend />
    <OpsDangerSourceAlert />
    <OpsAuditRiskPrediction />
    <OpsInsuranceEstimate />
    <OpsImproveSuggestion />
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
