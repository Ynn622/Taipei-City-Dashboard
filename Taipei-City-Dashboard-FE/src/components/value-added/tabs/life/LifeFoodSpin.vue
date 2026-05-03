<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	districtLocation,
	formatNumber,
	GEOJSON_FILES,
	geoJsonFeatures,
	haversineKm,
	normalizeLatLng,
	profileCategories,
	profileDistricts,
} from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const restaurants = ref([]);
const selectedIndex = ref(0);
const rotation = ref(0);
const showModal = ref(false);
const isSpinning = ref(false);

const cuisineCatalog = [
	{ label: "韓式", keywords: ["韓", "韓式", "韓廚", "豆腐家", "石鍋", "海苔飯捲", "年糕"] },
	{ label: "泰式", keywords: ["泰式", "泰泰", "瓦城", "湄南", "非常泰", "非越即泰", "泰國"] },
	{ label: "義式", keywords: ["義式", "義大利", "pasta", "pizza", "披薩", "比薩", "BELLINI", "PASTA", "PIZZA"] },
	{ label: "日式", keywords: ["日式", "日本", "壽司", "拉麵", "豬排", "丼", "勝勢", "壽司郎", "藏壽司"] },
	{ label: "港式", keywords: ["港式", "香港", "粵", "茶餐廳", "點點心", "飲茶", "添好運"] },
	{ label: "越式", keywords: ["越南", "河粉", "越式", "北越"] },
	{ label: "印度料理", keywords: ["印度", "咖哩", "番紅花"] },
	{ label: "火鍋", keywords: ["火鍋", "鍋", "海底撈", "築間", "涮涮", "麻辣"] },
	{ label: "燒肉", keywords: ["燒肉", "烤肉", "牛角", "乾杯", "燒肉SMILE"] },
	{ label: "蔬食", keywords: ["蔬食", "素食", "素", "蔬坊", "漢來蔬食", "健康"] },
	{ label: "早午餐", keywords: ["早午餐", "早餐", "漢堡", "QBURGER", "拉亞", "美而美"] },
	{ label: "咖啡甜點", keywords: ["咖啡", "甜點", "蛋糕", "星巴克", "路易莎", "多拿滋", "DONUT", "麵包"] },
	{ label: "台式小吃", keywords: ["小吃", "麵", "滷肉", "牛肉麵", "便當", "自助餐", "水餃", "飯"] },
	{ label: "美式速食", keywords: ["麥當勞", "肯德基", "漢堡王", "摩斯", "MOS", "炸雞"] },
];

onMounted(async () => {
	const collections = await store.fetchGeoJsonFiles(GEOJSON_FILES.goodRestaurants);
	restaurants.value = geoJsonFeatures(collections).map(toRestaurantItem).filter(Boolean);
	loading.value = false;
});

const profileText = computed(() => [
	...profileCategories(store.userProfile),
	...(store.userProfile.allergens || []).map((item) => `過敏原:${item}`),
	...(store.userProfile.foodSafetySensitivityTypes || []),
	store.userProfile.businessCategory,
	store.userProfile.notes,
].filter(Boolean).join("、"));

const options = computed(() => buildCuisineOptions(store.userProfile));
const selected = computed(() => options.value[selectedIndex.value % Math.max(options.value.length, 1)]);
const origin = computed(() => (
	normalizeLatLng(store.userProfile.userLocation) ||
	districtLocation(profileDistricts(store.userProfile)[0]) ||
	{ lat: 25.044808, lng: 121.536609 }
));
const originText = computed(() => {
	if (store.userProfile.userLocation) return "目前位置";
	const district = profileDistricts(store.userProfile)[0];
	return district || "臺北市中心點";
});

const matchedRestaurants = computed(() => {
	if (!selected.value) return [];
	return restaurants.value
		.map((item) => ({
			...item,
			distance: haversineKm(origin.value, item.location),
		}))
		.filter((item) => matchesCuisine(item, selected.value))
		.sort((a, b) => {
			if (a.distance !== null && b.distance !== null && a.distance !== b.distance) {
				return a.distance - b.distance;
			}
			if (a.distance !== null && b.distance === null) return -1;
			if (a.distance === null && b.distance !== null) return 1;
			return b.awardYear - a.awardYear || a.name.localeCompare(b.name, "zh-Hant");
		})
		.slice(0, 12);
});

watch(() => store.profileVersion, () => {
	selectedIndex.value = 0;
	showModal.value = false;
});

function spin() {
	if (options.value.length === 0 || isSpinning.value) return;
	const nextIndex = Math.floor(Math.random() * options.value.length);
	selectedIndex.value = nextIndex;
	rotation.value += 720 + nextIndex * (360 / options.value.length) + Math.random() * 28;
	showModal.value = false;
	isSpinning.value = true;
	window.setTimeout(() => {
		isSpinning.value = false;
		showModal.value = true;
	}, 850);
}

function toRestaurantItem(feature) {
	const props = feature?.properties || {};
	const coordinates = feature?.geometry?.coordinates;
	const location = Array.isArray(coordinates)
		? normalizeLatLng({ lat: coordinates[1], lng: coordinates[0] })
		: null;
	const name = props.restaurant_name || props.name;
	if (!name || !location) return null;
	return {
		name,
		city: props.city || "",
		district: props.district || "",
		address: props.address || "",
		rating: props.rating_result || "優",
		awardYear: Number(props.award_year || 0),
		location,
		searchText: [
			name,
			props.address,
			props.district,
			props.city,
		].filter(Boolean).join(" ").toLowerCase(),
	};
}

function buildCuisineOptions(profile) {
	const text = [
		...profileCategories(profile),
		profile.businessCategory,
		profile.notes,
	].filter(Boolean).join(" ");
	const blocked = allergenBlockedLabels(profile);
	const scored = cuisineCatalog
		.filter((item) => !blocked.has(item.label))
		.map((item, index) => ({
			...item,
			score: profileScore(item, text) + cuisineAvailability(item) + (cuisineCatalog.length - index) * 0.01,
		}))
		.sort((a, b) => b.score - a.score);
	const preferred = scored.slice(0, 8);
	return preferred.length >= 6 ? preferred : scored.slice(0, 6);
}

function allergenBlockedLabels(profile) {
	const allergens = (profile?.allergens || []).join("、");
	const blocked = new Set();
	if (/奶|乳|麩質|小麥/.test(allergens)) {
		blocked.add("咖啡甜點");
		blocked.add("義式");
	}
	if (/海鮮|甲殼|魚|蝦|蟹/.test(allergens)) {
		blocked.add("日式");
		blocked.add("泰式");
		blocked.add("越式");
	}
	if (/蛋/.test(allergens)) {
		blocked.add("早午餐");
		blocked.add("咖啡甜點");
	}
	return blocked;
}

function profileScore(cuisine, text) {
	if (!text) return 0;
	const normalized = text.toLowerCase();
	let score = 0;
	if (cuisine.keywords.some((keyword) => normalized.includes(keyword.toLowerCase()))) score += 8;
	if (/蔬|素|健康|低負擔/.test(text) && cuisine.label === "蔬食") score += 7;
	if (/肉|蛋白|聚餐/.test(text) && ["燒肉", "火鍋", "韓式"].includes(cuisine.label)) score += 4;
	if (/親子|家庭|快速|方便/.test(text) && ["台式小吃", "美式速食", "早午餐"].includes(cuisine.label)) score += 4;
	if (/異國|約會|朋友/.test(text) && ["義式", "泰式", "韓式", "日式"].includes(cuisine.label)) score += 4;
	return score;
}

function cuisineAvailability(cuisine) {
	return Math.min(6, restaurants.value.filter((item) => matchesCuisine(item, cuisine)).length / 10);
}

function matchesCuisine(restaurant, cuisine) {
	return cuisine.keywords.some((keyword) => restaurant.searchText.includes(keyword.toLowerCase()));
}

function distanceText(distance) {
	return distance === null ? "距離待補" : `${distance.toFixed(1)} km`;
}

function googleMapsUrl(restaurant) {
	const query = [
		restaurant.name,
		restaurant.address,
	].filter(Boolean).join(" ");
	return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}
</script>

<template>
  <ValueAddedCard
    title="今天吃什麼？"
    subtitle="依使用者輪廓產生餐飲類型，轉到結果後列出附近優良餐廳。"
    :loading="loading"
  >
    <template #action>
      <button
        class="spin-btn"
        :disabled="isSpinning || options.length === 0"
        @click="spin"
      >
        {{ isSpinning ? "轉動中" : "轉一下" }}
      </button>
    </template>

    <div class="wheel-wrap">
      <div class="wheel-arrow" />
      <div
        class="food-wheel"
        :style="{ transform: `rotate(${rotation}deg)` }"
      >
        <span
          v-for="(item, index) in options"
          :key="item.label"
          :style="{ transform: `rotate(${index * (360 / options.length)}deg) translateY(-58px)` }"
        >
          {{ item.label }}
        </span>
      </div>
      <div class="wheel-center">
        {{ selected?.label || "餐飲" }}
      </div>
    </div>

    <section class="hero-pick">
      <div>
        <span class="eyebrow">{{ originText }}附近 · {{ profileText || "均衡飲食" }}</span>
        <h4>{{ selected?.label || "餐型待補" }}</h4>
        <p>符合條件的優良餐廳 {{ formatNumber(matchedRestaurants.length, " 家") }}</p>
      </div>
      <button
        class="result-btn"
        type="button"
        :disabled="!selected"
        @click="showModal = true"
      >
        看餐廳
      </button>
    </section>
  </ValueAddedCard>

  <Teleport to="body">
    <div
      v-if="showModal"
      class="restaurant-modal-overlay"
      @click.self="showModal = false"
    >
      <section
        class="restaurant-overlay-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="food-spin-modal-title"
      >
        <header>
          <div>
            <span>{{ originText }}附近的優良餐廳</span>
            <h3 id="food-spin-modal-title">
              {{ selected?.label }}推薦
            </h3>
          </div>
          <button
            type="button"
            aria-label="關閉"
            @click="showModal = false"
          >
            ×
          </button>
        </header>

        <div class="restaurant-list">
          <article
            v-for="item in matchedRestaurants"
            :key="`${item.name}-${item.address}`"
          >
            <div>
              <h4>{{ item.name }}</h4>
              <p>{{ item.address }}</p>
            </div>
            <aside>
              <strong>{{ distanceText(item.distance) }}</strong>
              <span>{{ item.rating }} · {{ item.awardYear }} 年</span>
              <a
                class="map-link"
                :href="googleMapsUrl(item)"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="在 Google Maps 開啟"
              >
                <span aria-hidden="true">map</span>
                地圖
              </a>
            </aside>
          </article>
          <p
            v-if="matchedRestaurants.length === 0"
            class="empty-text"
          >
            目前優良餐廳資料中沒有符合這個餐飲類型的附近店家。
          </p>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped lang="scss">
.spin-btn,
.result-btn {
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);
  padding: 0.45rem 0.7rem;
  cursor: pointer;

  &:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
}

.wheel-wrap {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 210px;
}

.wheel-arrow {
  position: absolute;
  top: 2px;
  z-index: 3;
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-top: 24px solid #F2C94C;
}

.food-wheel {
  position: relative;
  width: 176px;
  aspect-ratio: 1;
  border-radius: 50%;
  border: solid 1px rgba(255, 255, 255, 0.16);
  background: conic-gradient(#30B68F, #1E88E5, #F2C94C, #E86F51, #7C5CFC, #72C6A4, #30B68F);
  display: grid;
  place-items: center;
  transition: transform 0.82s cubic-bezier(0.16, 0.88, 0.29, 1);

  span {
    position: absolute;
    width: 58px;
    color: #fff;
    font-size: 0.72rem;
    font-weight: 800;
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.55);
  }
}

.wheel-center {
  position: absolute;
  width: 76px;
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(9, 9, 9, 0.78);
  border: solid 1px rgba(255, 255, 255, 0.12);
  color: var(--color-normal-text);
  font-size: 0.82rem;
  font-weight: 800;
}

.hero-pick {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
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

.empty-text {
  margin: 0;
  color: var(--color-complement-text);
  line-height: 1.6;
}

.restaurant-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 30000;
  display: grid;
  place-items: start center;
  padding: 1rem;
  overflow-x: hidden;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.62);
}

.restaurant-overlay-panel {
  width: min(720px, 100%);
  height: min(680px, calc(100dvh - 2rem));
  max-height: calc(100vh - 2rem);
  max-height: calc(var(--vh) * 100 - 2rem);
  min-height: 0;
  margin: auto 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  overflow: hidden;
  border-radius: 8px;
  border: solid 1px rgba(255, 255, 255, 0.14);
  background: #171B1E;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);

  header {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 34px;
    gap: 1rem;
    align-items: start;
    padding: 1rem 1.1rem;
    border-bottom: solid 1px rgba(255, 255, 255, 0.09);
    overflow: visible;

    div {
      min-width: 0;
      overflow: visible;
    }

    span {
      display: block;
      color: var(--color-complement-text);
      font-size: 0.82rem;
      font-weight: 700;
      line-height: 1.6;
      white-space: normal;
      word-break: keep-all;
      overflow-wrap: break-word;
      overflow: visible;
    }

    h3 {
      margin: 0.2rem 0 0;
      color: var(--color-normal-text);
      font-size: 1.35rem;
      line-height: 1.35;
      overflow-wrap: anywhere;
      overflow: visible;
    }

    button {
      width: 34px;
      aspect-ratio: 1;
      border: solid 1px rgba(255, 255, 255, 0.12);
      border-radius: 7px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--color-normal-text);
      font-size: 1.35rem;
      cursor: pointer;
      overflow: visible;
    }
  }
}

.restaurant-list {
  display: grid;
  gap: 0.6rem;
  min-height: 0;
  overflow: auto;
  padding: 0.85rem;

  article {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(92px, auto);
    gap: 0.9rem;
    padding: 0.8rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.045);
    overflow: visible;

    > div {
      min-width: 0;
      overflow: visible;
    }

    h4 {
      margin: 0 0 0.25rem;
      color: var(--color-normal-text);
      font-size: 1rem;
      line-height: 1.45;
      overflow-wrap: anywhere;
      overflow: visible;
    }

    p {
      margin: 0;
      color: var(--color-complement-text);
      line-height: 1.5;
      overflow-wrap: anywhere;
      overflow: visible;
    }

    aside {
      display: grid;
      justify-items: end;
      align-content: center;
      gap: 0.32rem;
      color: var(--color-complement-text);
      min-width: 0;
      text-align: right;
      overflow: visible;

      strong {
        color: var(--color-normal-text);
        white-space: nowrap;
        overflow: visible;
      }

      span {
        line-height: 1.45;
        overflow-wrap: anywhere;
        overflow: visible;
      }

      .map-link {
        display: inline-flex;
        align-items: center;
        gap: 0.28rem;
        width: fit-content;
        margin-top: 0.1rem;
        padding: 0.34rem 0.48rem;
        border: solid 1px rgba(48, 182, 143, 0.42);
        border-radius: 7px;
        background: rgba(48, 182, 143, 0.12);
        color: var(--color-normal-text);
        font-size: 0.78rem;
        font-weight: 800;
        line-height: 1;
        overflow: visible;

        span {
          color: inherit;
          font-family: var(--font-icon);
          font-size: 1rem;
          line-height: 1;
          overflow: visible;
        }
      }
    }
  }
}

@media (max-width: 560px) {
  .hero-pick,
  .restaurant-list article {
    grid-template-columns: 1fr;
  }

  .restaurant-list article aside {
    justify-items: start;
    text-align: left;
  }
}
</style>
