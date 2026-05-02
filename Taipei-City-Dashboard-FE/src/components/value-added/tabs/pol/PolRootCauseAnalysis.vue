<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	sumRows,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const auditRows = ref([]);
const helpRows = ref([]);

onMounted(async () => {
	const [audit, help] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.postHelpAgency),
	]);
	auditRows.value = audit;
	helpRows.value = help;
	loading.value = false;
});

const rootCauses = computed(() => topRows(auditRows.value, 4));
const support = computed(() => topRows(helpRows.value, 3));
</script>

<template>
  <ValueAddedCard
    title="風險根源與影響"
    subtitle="比對違規熱點與事後求助節點，判斷事件影響範圍。"
    :loading="loading"
  >
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          違規事件
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(auditRows), " 件") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          求助節點
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(helpRows), " 處") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          主要熱點
        </div>
        <div class="summary-value">
          {{ rootCauses[0]?.label || "無資料" }}
        </div>
      </div>
    </div>
    <p class="note">
      熱點「{{ rootCauses[0]?.label || "待補資料" }}」附近可優先檢查「{{ support[0]?.label || "醫療/申訴" }}」資源是否足夠。
    </p>
  </ValueAddedCard>
</template>
