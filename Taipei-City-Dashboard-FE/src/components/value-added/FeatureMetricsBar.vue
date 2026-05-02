<script setup>
const metrics = [
	{ label: "全臺違規總數", value: "載入中..", id: "violation-total" },
	{ label: "本週高風險區域數", value: "載入中..", id: "high-risk-areas" },
	{ label: "優良農場供應商數", value: "載入中..", id: "good-farms" },
	{ label: "近期腹瀉就診趨勢", value: "載入中..", id: "diarrhea-trend" }
];
</script>

<template>
  <div class="metrics-bar">
    <div
      v-for="metric in metrics"
      :key="metric.id"
      class="metric-card"
    >
      <div class="metric-label">
        {{ metric.label }}
      </div>
      <div class="metric-value">
        {{ metric.value }}
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.metrics-bar {
  display: flex;
  gap: var(--font-s);
  flex-wrap: wrap;

  .metric-card {
    flex: 1 1 200px;
    background: var(--color-component-background);
    border: solid 1px var(--color-border);
    padding: var(--font-m);
    border-radius: 5px;
    text-align: left;

    .metric-label {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--color-complement-text);
      margin-bottom: 0.35rem;
    }

    .metric-value {
      font-size: 1.45rem;
      font-weight: bold;
      color: var(--color-normal-text);
      letter-spacing: 0.02em;
    }
  }
}
</style>
