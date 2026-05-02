<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const mode = ref("行政區");
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.healthAuditViolation);
	loading.value = false;
});

const hotspots = computed(() => topRows(rows.value, 10));

const chartOptions = computed(() => ({
	chart: { type: "treemap", background: "transparent", toolbar: { show: false }, fontFamily: "inherit" },
	theme: { mode: "dark" },
	colors: ["#D84C73", "#E86F51", "#F2994A", "#F2C94C", "#30B68F"],
	dataLabels: { enabled: true, style: { fontSize: "13px", fontWeight: 700 }, formatter: (text, op) => [text, op.value + " 件"] },
	plotOptions: {
		treemap: {
			distributed: true,
			enableShades: false,
		},
	},
	tooltip: { theme: "dark", y: { formatter: (v) => v + " 件" } },
	legend: { show: false },
}));

const chartSeries = computed(() => [{
	data: hotspots.value.map((r) => ({ x: r.label, y: r.value })),
}]);
</script>

<template>
  <ValueAddedCard
    title="食安風險熱區"
    subtitle="以衛生稽核違規分布建立熱區排序，方塊面積代表違規件數。"
    :loading="loading"
  >
    <template #action>
      <select v-model="mode">
        <option>行政區</option>
        <option>時段</option>
      </select>
    </template>
    <apexchart
      v-if="!loading && chartSeries[0].data.length"
      type="treemap"
      width="100%"
      height="240"
      :options="chartOptions"
      :series="chartSeries"
    />
    <p class="note">
      方塊愈大代表違規件數愈高；前段區域建議安排跨資料源覆核。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
select {
  border: solid 1px var(--color-border);
  border-radius: 5px;
  background: var(--color-background);
  color: var(--color-normal-text);
  padding: 0.35rem 0.5rem;
  font-size: 0.85rem;
}
</style>
