<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	trendSummary,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.infectious);
	loading.value = false;
});

const trend = computed(() => trendSummary(rows.value));
</script>

<template>
  <ValueAddedCard
    title="趨勢分析"
    subtitle="標示近期腹瀉就診人次的劇烈變化，供政策預警使用。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          最新週
        </div>
        <div class="summary-value">
          {{ trend.hasData ? formatNumber(trend.latest, " 人次") : "無資料" }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          週變化
        </div>
        <div class="summary-value">
          {{ trend.direction }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          變化量
        </div>
        <div class="summary-value">
          {{ trend.delta !== null ? formatNumber(Math.abs(trend.delta), " 人次") : "無資料" }}
        </div>
      </div>
    </div>
    <p class="note">
      {{ trend.delta === null ? "目前未取得腹瀉就診時間序列，需待 component 502 chart data 可用後才可判讀趨勢。" : Math.abs(trend.delta) > 500 ? "變化幅度較大，建議同步檢查稽核違規與市場來源。" : "近期趨勢相對平穩，維持例行監測即可。" }}
    </p>
  </ValueAddedCard>
</template>
