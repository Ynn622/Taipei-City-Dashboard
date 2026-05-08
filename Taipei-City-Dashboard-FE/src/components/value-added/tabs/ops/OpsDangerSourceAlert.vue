<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import {
	GEOJSON_FILES,
	districtLocation,
	formatNumber,
	haversineKm,
	rowLatLng,
} from "../../valueAddedAnalytics";

const DEFAULT_ORIGIN = { lat: 25.044808, lng: 121.536609 };
const SEARCH_RADII_KM = [3, 5, 10, 20];
const store = useValueAddedStore();
const loading = ref(true);
const rows = ref([]);

onMounted(async () => {
	rows.value = await fetchFoodAuditRows();
	loading.value = false;
});

const origin = computed(() => (
	store.userProfile.userLocation ||
	districtLocation(store.userProfile.focusDistricts?.[0]) ||
	DEFAULT_ORIGIN
));
const nearbyResult = computed(() => nearbyRows(rows.value, origin.value));
const dangerSources = computed(() => rankFoodRiskCategories(nearbyResult.value.rows).slice(0, 6));
const nearbyLabel = computed(() => {
	const district = store.userProfile.focusDistricts?.[0];
	const basis = store.userProfile.userLocation ? "目前位置" : district || "臺北市中心點";
	return `${basis}周邊 ${nearbyResult.value.radiusKm} km`;
});

async function fetchFoodAuditRows() {
	const collections = await store.fetchGeoJsonFiles(GEOJSON_FILES.foodAudit);
	return collections.flatMap((collection) => collection.features || [])
		.map((feature) => ({
			...(feature.properties || {}),
			_geometry: feature.geometry,
		}));
}

function nearbyRows(sourceRows, center) {
	for (const radiusKm of SEARCH_RADII_KM) {
		const rowsInRadius = sourceRows
			.map((row) => ({
				...row,
				_distance: haversineKm(center, rowLatLng(row)),
			}))
			.filter((row) => row._distance !== null && row._distance <= radiusKm);
		if (rowsInRadius.length > 0) {
			return { rows: rowsInRadius, radiusKm };
		}
	}
	return {
		rows: sourceRows.map((row) => ({
			...row,
			_distance: haversineKm(center, rowLatLng(row)),
		})).filter((row) => row._distance !== null),
		radiusKm: SEARCH_RADII_KM.at(-1),
	};
}

function rankFoodRiskCategories(sourceRows) {
	const totals = new Map();
	sourceRows.forEach((row) => {
		const label = foodRiskCategory(row);
		const bucket = totals.get(label) || {
			label,
			count: 0,
			nearest: Number.POSITIVE_INFINITY,
			examples: new Set(),
		};
		bucket.count += Number(row.violation_count || 1);
		bucket.nearest = Math.min(bucket.nearest, Number(row._distance || Number.POSITIVE_INFINITY));
		if (row.sample_item) bucket.examples.add(cleanSampleItem(row.sample_item));
		totals.set(label, bucket);
	});
	return [...totals.values()]
		.map((item) => ({
			...item,
			exampleText: [...item.examples].filter(Boolean).slice(0, 2).join("、") || "抽驗不合格",
		}))
		.sort((a, b) => b.count - a.count || a.nearest - b.nearest)
		.map((item, index) => ({ ...item, rank: index + 1 }));
}

function foodRiskCategory(row) {
	const text = [
		row.product_category,
		row.sample_item,
		row.project_name,
		row.violation_reason,
	].filter(Boolean).join(" ");
	const normalized = text.replace(/\s+/g, "");
	const keywordGroups = [
		{ label: "魚類/水產", keywords: ["魚", "水產", "鮭", "鮪", "鱈", "蝦", "蟹", "貝", "蚵", "牡蠣", "花枝", "魷"] },
		{ label: "蛋品", keywords: ["蛋", "雞蛋", "鴨蛋"] },
		{ label: "豬肉", keywords: ["豬", "豬肉"] },
		{ label: "牛肉", keywords: ["牛", "牛肉"] },
		{ label: "雞肉", keywords: ["雞", "雞肉", "禽"] },
		{ label: "羊肉", keywords: ["羊", "羊肉"] },
		{ label: "蔬菜", keywords: ["菜", "蔬", "葉菜", "包葉", "根菜", "瓜菜", "豆菜", "菇", "蘑菇", "竹笙"] },
		{ label: "水果", keywords: ["果", "水果", "柑", "莓", "棗", "瓜", "蜜餞"] },
		{ label: "豆製品", keywords: ["豆干", "豆乾", "豆腐", "大豆", "豆製"] },
		{ label: "米麵/穀物", keywords: ["米", "麵", "粉", "穀", "雜糧", "澱粉"] },
		{ label: "乳品", keywords: ["乳", "奶", "起司", "乳酪"] },
		{ label: "茶/飲品", keywords: ["茶", "飲料", "咖啡"] },
		{ label: "調味/香辛料", keywords: ["辣椒", "香辛料", "調味", "醬", "油"] },
	];
	const matched = keywordGroups.find((group) => group.keywords.some((keyword) => normalized.includes(keyword)));
	if (matched) return matched.label;
	if (normalized.includes("農藥殘留")) return "蔬果類";
	if (normalized.includes("食品添加物")) return "加工食品";
	if (normalized.includes("食品微生物")) return "即食/餐飲食品";
	return row.product_category || "其他食品";
}

function cleanSampleItem(value) {
	return String(value)
		.replace(/\s+/g, " ")
		.replace(/[（(].*?[）)]/g, "")
		.trim();
}
</script>

<template>
  <ValueAddedCard
    title="危險來源迴避"
    :subtitle="`${nearbyLabel} 的風險食物類別排行。`"
    :loading="loading"
  >
    <div class="avoid-list">
      <div
        v-for="item in dangerSources"
        :key="item.label"
        class="avoid-item"
      >
        <div>
          <span>#{{ item.rank }} {{ item.label }}</span>
          <small>{{ item.exampleText }} / 最近 {{ item.nearest.toFixed(1) }} km</small>
        </div>
        <strong>{{ formatNumber(item.count, " 件") }}</strong>
      </div>
    </div>
    <p class="note">
      依食品抽驗不合格點位統計附近食物類別；若最近半徑內沒有資料，會自動擴大搜尋範圍。
    </p>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.avoid-list {
  display: grid;
  gap: 0.58rem;
}

.avoid-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.7rem;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.045);

  span {
    display: block;
    color: var(--color-normal-text);
    font-weight: 800;
  }

  small {
    color: var(--color-complement-text);
  }

	  strong {
	    color: #E86F51;
	    font-size: 1.05rem;
	  }
	}

.note {
  margin: 0;
  color: var(--color-complement-text);
  font-size: 0.78rem;
  line-height: 1.55;
}
</style>
