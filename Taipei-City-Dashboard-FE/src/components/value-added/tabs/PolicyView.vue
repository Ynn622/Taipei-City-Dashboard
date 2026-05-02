<script setup>
import PolRiskHeatmap from "./pol/PolRiskHeatmap.vue";
import PolRootCauseAnalysis from "./pol/PolRootCauseAnalysis.vue";
import PolAuditPriority from "./pol/PolAuditPriority.vue";
import PolTrendAnalysis from "./pol/PolTrendAnalysis.vue";
import PolEventScope from "./pol/PolEventScope.vue";
import PolImproveSuggestion from "./pol/PolImproveSuggestion.vue";
</script>
<template>
  <div class="tab-view">
    <PolRiskHeatmap />
    <PolRootCauseAnalysis />
    <PolAuditPriority />
    <PolTrendAnalysis />
    <PolEventScope />
    <PolImproveSuggestion />
  </div>
</template>

<style scoped lang="scss">
.tab-view {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

@media (max-width: 860px) {
  .tab-view {
    grid-template-columns: 1fr;
  }
}
</style>
