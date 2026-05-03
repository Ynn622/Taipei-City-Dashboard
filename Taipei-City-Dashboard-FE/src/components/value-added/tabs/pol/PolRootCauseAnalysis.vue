<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	rowLabel,
	sumRows,
	topRows,
	unwrapRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const auditRows = ref([]);
const helpRows = ref([]);
const selectedRegion = ref("全部");

onMounted(async () => {
	const [audit, help] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
		store.fetchComponentData(COMPONENT_IDS.postHelpAgency),
	]);
	auditRows.value = audit;
	helpRows.value = help;
	loading.value = false;
});

const regionOptions = computed(() => topRows(auditRows.value, 99).map((item) => item.label));
const filteredAuditRows = computed(() => filterRowsByRegion(auditRows.value, selectedRegion.value));
const filteredHelpRows = computed(() => {
	if (!selectedRegion.value || selectedRegion.value === "全部") return unwrapRows(helpRows.value);
	const raw = helpRows.value?.rawRows;
	if (raw && Array.isArray(raw)) {
		const filtered = raw.filter((row) => row?.district === selectedRegion.value);
		const totals = new Map();
		filtered.forEach((row) => {
			const type = row?.agency_type || row?.agency_group || "未分類";
			totals.set(type, (totals.get(type) || 0) + 1);
		});
		return [...totals.entries()].map(([x_axis, data]) => ({ x_axis, data }));
	}
	return filterRowsByRegion(helpRows.value, selectedRegion.value);
});
const rootCauses = computed(() => topRows(filteredAuditRows.value, 4));
const support = computed(() => topRows(filteredHelpRows.value.length > 0 ? filteredHelpRows.value : unwrapRows(helpRows.value), 3));

function filterRowsByRegion(rows, region) {
	if (!region || region === "全部") return unwrapRows(rows);
	return unwrapRows(rows).filter((row) => rowLabel(row) === region);
}
</script>

<template>
  <ValueAddedCard
    title="風險根源與影響"
    subtitle="比對違規熱點與事後求助節點，判斷事件影響範圍。"
    :loading="loading"
  >
    <template #action>
      <select
        v-model="selectedRegion"
        class="region-select"
      >
        <option value="全部">
          全部地區
        </option>
        <option
          v-for="region in regionOptions"
          :key="region"
          :value="region"
        >
          {{ region }}
        </option>
      </select>
    </template>
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-label">
          違規事件
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(filteredAuditRows), " 件") }}
        </div>
      </div>
      <div class="summary-item">
        <div class="summary-label">
          求助資源
        </div>
        <div class="summary-value">
          {{ formatNumber(sumRows(filteredHelpRows.length > 0 ? filteredHelpRows : helpRows), " 處") }}
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
      求助資源是事件後可提供諮詢、通報、醫療或申訴協助的機構節點；熱點「{{ rootCauses[0]?.label || "待補資料" }}」附近可優先檢查「{{ support[0]?.label || "醫療/申訴" }}」資源是否足夠。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.region-select {
  min-height: 32px;
  min-width: 116px;
  border: solid 1px var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-normal-text);
  padding: 0.28rem 0.5rem;
  font-size: 0.82rem;
}
</style>
