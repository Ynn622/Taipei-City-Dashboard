<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	COMPONENT_IDS,
	formatNumber,
	profileCategories,
	sortByDistanceThenDistrict,
	topRows,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);
const selectedIndex = ref(0);
const rotation = ref(0);

onMounted(async () => {
	rows.value = await store.fetchComponentData(COMPONENT_IDS.goodRestaurants);
	loading.value = false;
});

const cuisineHints = ["便當/簡餐", "麵飯小吃", "火鍋湯品", "蔬食輕食", "家庭料理", "市場熟食"];
const options = computed(() => topRows(rows.value, 8).map((item, index) => ({
	...item,
	cuisine: cuisineHints[index % cuisineHints.length],
})));
const selected = computed(() => options.value[selectedIndex.value % Math.max(options.value.length, 1)]);
const nearbyRestaurants = computed(() => sortByDistanceThenDistrict(rows.value, store.userProfile.userLocation, {
	fallbackDistricts: store.userProfile.focusDistricts,
}).filter((item) => !selected.value || item.label === selected.value.label).slice(0, 5));
const preference = computed(() => profileCategories(store.userProfile).join("、") || "均衡飲食");

function spin() {
	if (options.value.length === 0) return;
	selectedIndex.value = Math.floor(Math.random() * options.value.length);
	rotation.value += 360 + selectedIndex.value * 42;
}
</script>

<template>
  <ValueAddedCard
    title="今天吃什麼？"
    subtitle="用有箭頭輪盤選出餐飲類型，再列出附近且屬優良名單的選項。"
    :loading="loading"
  >
    <template #action>
      <button
        class="spin-btn"
        @click="spin"
      >
        轉一下
      </button>
    </template>
    <div class="wheel-wrap">
      <div class="wheel-arrow" />
      <div
        class="food-wheel"
        :style="{ transform: `rotate(${rotation}deg)` }"
      >
        <span
          v-for="item in options.slice(0, 6)"
          :key="item.label"
        >
          {{ item.cuisine }}
        </span>
      </div>
    </div>
    <section class="hero-pick">
      <div>
        <span class="eyebrow">偏好：{{ preference }}</span>
        <h4>{{ selected?.cuisine || "餐型待補" }}</h4>
        <p>{{ selected?.label || "依目前資料挑選較穩定的外食區域" }}</p>
      </div>
      <div class="score-ring">
        <strong>{{ selected?.value || "--" }}</strong>
        <span>優良數</span>
      </div>
    </section>
    <div class="nearby-list">
      <div
        v-for="item in nearbyRestaurants"
        :key="item.label"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.distanceText }}</strong>
        <small>{{ formatNumber(item.value, " 家") }}</small>
      </div>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.spin-btn {
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);
  padding: 0.45rem 0.7rem;
  cursor: pointer;
}

.wheel-wrap {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 190px;
}

.wheel-arrow {
  position: absolute;
  top: 2px;
  z-index: 2;
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-top: 24px solid #F2C94C;
}

.food-wheel {
  width: 168px;
  aspect-ratio: 1;
  border-radius: 50%;
  border: solid 1px rgba(255, 255, 255, 0.14);
  background: conic-gradient(#30B68F, #72C6A4, #1E88E5, #F2C94C, #F2994A, #E86F51, #30B68F);
  display: grid;
  place-items: center;
  transition: transform 0.8s ease;

  span {
    grid-area: 1 / 1;
    color: #fff;
    font-size: 0.76rem;
    font-weight: 800;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }
}

.hero-pick {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 86px;
  gap: 0.9rem;
  align-items: center;
  padding: 0.9rem;
  border-radius: 8px;
  background: rgba(9, 9, 9, 0.28);

  h4 {
    margin: 0.15rem 0 0.2rem;
    color: var(--color-normal-text);
    font-size: 1.7rem;
  }

  p,
  .eyebrow {
    color: var(--color-complement-text);
  }
}

.score-ring {
  width: 82px;
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  align-content: center;
  background: rgba(48, 182, 143, 0.12);

  strong {
    color: var(--color-normal-text);
    font-size: 1.45rem;
    line-height: 1;
  }

  span {
    color: var(--color-complement-text);
    font-size: 0.72rem;
  }
}

.nearby-list {
  display: grid;
  gap: 0.5rem;

  div {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto auto;
    gap: 0.55rem;
    padding: 0.55rem 0.65rem;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.045);
  }
}
</style>
