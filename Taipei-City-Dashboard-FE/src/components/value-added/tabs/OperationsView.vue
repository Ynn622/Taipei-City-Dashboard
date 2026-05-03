<script setup>
import OpsSupplierRecommend from "./ops/OpsSupplierRecommend.vue";
import OpsDangerSourceAlert from "./ops/OpsDangerSourceAlert.vue";
import OpsAuditRiskPrediction from "./ops/OpsAuditRiskPrediction.vue";
import OpsInsuranceEstimate from "./ops/OpsInsuranceEstimate.vue";
import OpsImproveSuggestion from "./ops/OpsImproveSuggestion.vue";
</script>
<template>
  <div class="tab-view">
    <div class="tab-left">
      <OpsSupplierRecommend />
    </div>
    <div class="tab-right">
      <OpsAuditRiskPrediction />
      <OpsInsuranceEstimate />
      <OpsDangerSourceAlert />
    </div>
    <div class="tab-bottom">
      <OpsImproveSuggestion />
    </div>
  </div>
</template>

<style scoped lang="scss">
.tab-view {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
  grid-template-areas:
    "supplier risk"
    "llm llm";
  gap: 1rem;
  align-items: stretch;
}

.tab-left {
  grid-area: supplier;
  display: flex;
  min-width: 0;
}

.tab-left :deep(.value-card) {
  width: 100%;
  height: 100%;
}

.tab-right {
  grid-area: risk;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.tab-bottom {
  grid-area: llm;
  min-width: 0;
}

@media (max-width: 860px) {
  .tab-view {
    grid-template-columns: 1fr;
    grid-template-areas:
      "supplier"
      "risk"
      "llm";
  }
}
</style>
