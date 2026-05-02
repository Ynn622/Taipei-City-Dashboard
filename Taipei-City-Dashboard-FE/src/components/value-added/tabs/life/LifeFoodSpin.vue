<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	maxValue,
	profileCategories,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const violationRows = ref([]);
const selectedIndex = ref(0);

onMounted(async () => {
	const [restaurants, violations] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.goodRestaurants),
		store.fetchComponentData(COMPONENT_IDS.healthAuditViolation),
	]);
	rows.value = restaurants;
	violationRows.value = violations;
	loading.value = false;
});

const moods = ["清爽簡單", "熱食安心", "多人聚餐", "快速補給", "散步覓食", "下班犒賞"];
const cuisineHints = ["便當/簡餐", "麵飯小吃", "火鍋湯品", "蔬食輕食", "家庭料理", "市場熟食"];

const options = computed(() => {
	const goodRows = topRows(rows.value, 8);
	const violationMap = new Map(topRows(violationRows.value, 99).map((item) => [item.label, item.value]));
	const highestGood = maxValue(goodRows) || 1;
	const highestViolation = maxValue([...violationMap.entries()].map(([label, value]) => ({ label, value }))) || 1;

	return goodRows
		.map((item, index) => {
			const violation = violationMap.get(item.label) || 0;
			const coverageScore = Math.round((item.value / highestGood) * 64);
			const riskPenalty = Math.round((violation / highestViolation) * 18);
			const preferenceBonus = profileCategories(store.userProfile).length > 0 ? 8 : 4;
			const score = Math.max(42, Math.min(98, 28 + coverageScore + preferenceBonus - riskPenalty));

			return {
				...item,
				score,
				violation,
				mood: moods[index % moods.length],
				cuisine: cuisineHints[index % cuisineHints.length],
			};
		})
		.sort((a, b) => b.score - a.score);
});
const selected = computed(() => options.value[selectedIndex.value % Math.max(options.value.length, 1)]);
const preference = computed(() => profileCategories(store.userProfile).join("、") || "均衡飲食");
const backupOptions = computed(() => options.value.filter((item) => item.label !== selected.value?.label).slice(0, 2));
const matchLevel = computed(() => {
	if (!selected.value) return "無資料";
	if (selected.value.score >= 86) return "很適合";
	if (selected.value.score >= 72) return "穩定選";
	return "可考慮";
});
const riskLabel = computed(() => {
	if (!selected.value) return "無資料";
	if (selected.value.violation === 0) return "未見主要違規熱點";
	if (selected.value.score >= 78) return "可吃，留意店家公告";
	return "建議避開高峰與生食";
});
const detailRows = computed(() => [
	{ label: "情境", value: selected.value?.mood || "無資料" },
	{ label: "餐型", value: selected.value?.cuisine || "無資料" },
	{ label: "偏好", value: preference.value },
]);
const reasonChips = computed(() => {
	if (!selected.value) return ["尚無可推薦資料"];
	return [
		`優良餐廳 ${formatNumber(selected.value.value, " 家")}`,
		riskLabel.value,
		`偏好：${preference.value}`,
	];
});

function spin() {
	if (options.value.length === 0) return;
	selectedIndex.value = Math.floor(Math.random() * options.value.length);
}
</script>

<template>
  <ValueAddedCard
    title="今天吃什麼？"
    subtitle="結合優良餐廳分布與偏好輪廓，提供一個可執行選項。"
    :loading="loading"
  >
    <template #action>
      <button
        class="spin-btn"
        @click="spin"
      >
        換一個
      </button>
    </template>
    <div class="food-picker">
      <section class="hero-pick">
        <div>
          <span class="eyebrow">{{ matchLevel }}</span>
          <h4>{{ selected?.label || "無資料" }}</h4>
          <p>{{ selected?.mood || "依目前資料挑選較穩定的外食區域" }} · {{ selected?.cuisine || "餐型待補" }}</p>
        </div>
        <div class="score-ring">
          <strong>{{ selected?.score || "--" }}</strong>
          <span>適合度</span>
        </div>
      </section>

      <div class="detail-grid">
        <div
          v-for="item in detailRows"
          :key="item.label"
          class="detail-item"
        >
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>

      <div class="reason-list">
        <span
          v-for="reason in reasonChips"
          :key="reason"
        >
          {{ reason }}
        </span>
      </div>

      <div class="backup-list">
        <div class="backup-title">
          備案
        </div>
        <button
          v-for="item in backupOptions"
          :key="item.label"
          type="button"
          @click="selectedIndex = options.findIndex((option) => option.label === item.label)"
        >
          <span>{{ item.label }}</span>
          <strong>{{ item.score }} 分</strong>
        </button>
      </div>

      <p class="note">
        先挑優良餐廳覆蓋高的區域，再用違規熱點做扣分；{{ riskLabel }}。
      </p>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.food-picker {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.hero-pick {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 86px;
  gap: 0.9rem;
  align-items: center;
  padding: 0.9rem;
  border: solid 1px rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(9, 9, 9, 0.28);

  h4 {
    margin: 0.15rem 0 0.2rem;
    color: var(--color-normal-text);
    font-size: 1.8rem;
    line-height: 1.1;
    font-weight: 800;
  }

  p {
    margin: 0;
    color: var(--color-complement-text);
    font-size: 0.88rem;
    line-height: 1.45;
  }
}

.eyebrow {
  color: var(--color-highlight);
  font-size: 0.78rem;
  font-weight: 700;
}

.score-ring {
  width: 82px;
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  align-content: center;
  border: solid 1px rgba(255, 255, 255, 0.12);
  border-radius: 50%;
  background: rgba(48, 182, 143, 0.12);

  strong {
    color: var(--color-normal-text);
    font-size: 1.45rem;
    line-height: 1;
  }

  span {
    margin-top: 0.2rem;
    color: var(--color-complement-text);
    font-size: 0.72rem;
  }
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}

.detail-item {
  min-width: 0;
  padding: 0.62rem 0.65rem;
  border: solid 1px rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.035);

  span {
    display: block;
    color: var(--color-complement-text);
    font-size: 0.76rem;
    line-height: 1.35;
  }

  strong {
    display: block;
    margin-top: 0.2rem;
    color: var(--color-normal-text);
    font-size: 0.92rem;
    line-height: 1.3;
    overflow-wrap: anywhere;
  }
}

.reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;

  span {
    padding: 0.38rem 0.55rem;
    border: solid 1px rgba(255, 255, 255, 0.09);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.045);
    color: var(--color-normal-text);
    font-size: 0.8rem;
    line-height: 1.35;
  }
}

.backup-list {
  display: grid;
  grid-template-columns: auto repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  align-items: center;
}

.backup-title {
  color: var(--color-complement-text);
  font-size: 0.78rem;
  font-weight: 700;
}

.backup-list button,
.spin-btn {
  min-height: 34px;
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
  }
}

.backup-list button {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  min-width: 0;
  padding: 0.48rem 0.6rem;
  font-size: 0.82rem;

  span {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.spin-btn {
  padding: 0.48rem 0.75rem;
  font-size: 0.86rem;
  font-weight: 700;
}

@media (max-width: 640px) {
  .hero-pick,
  .detail-grid,
  .backup-list {
    grid-template-columns: 1fr;
  }

  .score-ring {
    width: 74px;
    justify-self: start;
  }
}
</style>
