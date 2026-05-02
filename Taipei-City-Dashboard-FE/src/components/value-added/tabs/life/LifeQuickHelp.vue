<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	maxValue,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.postHelpAgency);
	loading.value = false;
});

const helpTypes = computed(() => topRows(rows.value, 5));
const max = computed(() => maxValue(helpTypes.value));
</script>

<template>
  <ValueAddedCard
    title="快速求助"
    subtitle="彙整醫療、申訴與消費爭議支援節點。"
    :loading="loading"
  >
    <div class="rank-list">
      <div
        v-for="item in helpTypes"
        :key="item.label"
        class="rank-row"
      >
        <span>{{ item.label }}</span>
        <strong>{{ formatNumber(item.value, " 處") }}</strong>
        <div class="bar-track">
          <span
            class="bar-fill"
            :style="{ width: `${(item.value / max) * 100}%` }"
          />
        </div>
      </div>
    </div>
    <p class="note">
      發生疑似食安事件時，先就醫保留診斷與消費憑證，再依所在地向衛生局或消保單位通報。
    </p>
  </ValueAddedCard>
</template>
