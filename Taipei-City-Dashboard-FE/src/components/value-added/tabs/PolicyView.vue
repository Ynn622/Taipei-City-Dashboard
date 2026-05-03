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
    <div class="tab-main">
      <div class="tab-column">
        <PolRiskHeatmap />
        <PolAuditPriority />
      </div>
      <div class="tab-column balanced-column">
        <PolRootCauseAnalysis />
        <PolEventScope />
        <PolTrendAnalysis />
      </div>
    </div>
    <div class="tab-full">
      <PolImproveSuggestion />
    </div>
  </div>
</template>

<style scoped lang="scss">
.tab-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tab-main {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.tab-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

@media (max-width: 860px) {
  .tab-main {
    grid-template-columns: 1fr;
    align-items: start;
  }
}
</style>
