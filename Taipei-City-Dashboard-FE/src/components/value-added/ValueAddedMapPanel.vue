<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import mapboxGl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import mapStyle from "../../assets/configs/mapbox/mapStyle";

const props = defineProps({
	points: {
		type: Array,
		default: () => [],
	},
	circles: {
		type: Array,
		default: () => [],
	},
	lines: {
		type: Array,
		default: () => [],
	},
	districts: {
		type: Array,
		default: () => [],
	},
	areaLevel: {
		type: String,
		default: "district",
		validator: (value) => ["district", "city"].includes(value),
	},
	selectedLabel: {
		type: String,
		default: "",
	},
	height: {
		type: Number,
		default: 260,
	},
});

const emit = defineEmits(["select"]);

const mapEl = ref(null);
const mapReady = ref(false);
const districtBoundary = ref(null);
const accessToken = import.meta.env.VITE_MAPBOXTOKEN;
let map = null;
let resizeObserver = null;

const hasMapToken = computed(() => Boolean(accessToken));
const hasGeoData = computed(() => pointFeatures.value.length > 0 || circleFeatures.value.length > 0 || lineFeatures.value.length > 0 || districtFeatures.value.length > 0);

const pointFeatures = computed(() => props.points
	.filter((item) => isValidCoordinate(item))
	.map((item) => ({
		type: "Feature",
		geometry: {
			type: "Point",
			coordinates: [Number(item.lng), Number(item.lat)],
		},
		properties: {
			label: item.label || "",
			value: Number(item.value || 0),
			color: item.color || "#E86F51",
			radius: Number(item.radius || 12),
			isSelected: item.label === props.selectedLabel,
		},
	})));

const circleFeatures = computed(() => props.circles
	.filter((item) => isValidCoordinate(item) && Number(item.radiusKm) > 0)
	.map((item) => ({
		type: "Feature",
		geometry: circlePolygon([Number(item.lng), Number(item.lat)], Number(item.radiusKm)),
		properties: {
			label: item.label || "",
			color: item.color || "#30B68F",
			opacity: Number(item.opacity ?? 0.18),
		},
	})));

const lineFeatures = computed(() => props.lines
	.map((item) => {
		const coordinates = lineCoordinates(item);
		if (!coordinates) return null;
		return {
			type: "Feature",
			geometry: {
				type: "LineString",
				coordinates,
			},
			properties: {
				label: item.label || "",
				value: Number(item.value || 0),
				color: item.color || "#72C6A4",
				opacity: Number(item.opacity ?? 0.78),
				width: Number(item.width || 2.5),
				isSelected: item.label === props.selectedLabel,
			},
		};
	})
	.filter(Boolean));

const pointCollection = computed(() => ({
	type: "FeatureCollection",
	features: pointFeatures.value,
}));

const circleCollection = computed(() => ({
	type: "FeatureCollection",
	features: circleFeatures.value,
}));

const lineCollection = computed(() => ({
	type: "FeatureCollection",
	features: lineFeatures.value,
}));

const districtFeatures = computed(() => {
	const boundary = districtBoundary.value;
	if (!boundary?.features?.length || props.districts.length === 0) return [];
	const districtValueMap = new Map(
		props.districts.map((item) => [item.label, item]),
	);
	return boundary.features.map((feature) => {
		const label = props.areaLevel === "city"
			? feature.properties?.PNAME || ""
			: feature.properties?.TNAME || feature.properties?.district_name || "";
		const district = districtValueMap.get(label);
		const value = Number(district?.value || 0);
		return {
			...feature,
			properties: {
				...feature.properties,
				label,
				value,
				color: district?.color || "#30B68F",
				opacity: Number(district?.opacity ?? (value > 0 ? 0.32 : 0.08)),
				isSelected: label === props.selectedLabel,
			},
		};
	});
});

const districtCollection = computed(() => ({
	type: "FeatureCollection",
	features: districtFeatures.value,
}));

onMounted(() => {
	if (!hasMapToken.value || !mapEl.value) return;
	fetchDistrictBoundary();
	mapboxGl.accessToken = accessToken;
	map = new mapboxGl.Map({
		container: mapEl.value,
		style: mapStyle,
		center: [121.536609, 25.044808],
		zoom: 10,
		minZoom: 8,
		maxZoom: 16,
		maxBounds: [
			[121.2825, 24.6961],
			[122.0073, 25.2979],
		],
		attributionControl: false,
		interactive: true,
	});

	map.addControl(new mapboxGl.NavigationControl({ showCompass: false }), "top-right");
	map.on("load", () => {
		mapReady.value = true;
		addLayers();
		updateData();
		fitToData();
	});

	resizeObserver = new ResizeObserver(() => {
		map?.resize();
	});
	resizeObserver.observe(mapEl.value);
});

onBeforeUnmount(() => {
	resizeObserver?.disconnect();
	resizeObserver = null;
	map?.remove();
	map = null;
});

watch(
	[pointCollection, circleCollection, lineCollection, districtCollection],
	() => {
		updateData();
		fitToData();
	},
	{ deep: true },
);

watch(
	() => props.selectedLabel,
	() => {
		updateData();
	},
);

function addLayers() {
	if (!map || map.getSource("value-added-points")) return;
	map.addSource("value-added-districts", {
		type: "geojson",
		data: districtCollection.value,
	});
	map.addSource("value-added-circles", {
		type: "geojson",
		data: circleCollection.value,
	});
	map.addSource("value-added-lines", {
		type: "geojson",
		data: lineCollection.value,
	});
	map.addSource("value-added-points", {
		type: "geojson",
		data: pointCollection.value,
	});
	map.addLayer({
		id: "value-added-district-fill",
		type: "fill",
		source: "value-added-districts",
		paint: {
			"fill-color": ["get", "color"],
			"fill-opacity": [
				"case",
				["get", "isSelected"],
				0.82,
				["get", "opacity"],
			],
		},
	});
	map.addLayer({
		id: "value-added-district-line",
		type: "line",
		source: "value-added-districts",
		paint: {
			"line-color": [
				"case",
				["get", "isSelected"],
				"#ffffff",
				"rgba(255, 255, 255, 0.36)",
			],
			"line-width": [
				"case",
				["get", "isSelected"],
				2,
				0.8,
			],
		},
	});
	map.addLayer({
		id: "value-added-circle-fill",
		type: "fill",
		source: "value-added-circles",
		paint: {
			"fill-color": ["get", "color"],
			"fill-opacity": ["get", "opacity"],
		},
	});
	map.addLayer({
		id: "value-added-circle-line",
		type: "line",
		source: "value-added-circles",
		paint: {
			"line-color": ["get", "color"],
			"line-opacity": 0.72,
			"line-width": 1.5,
		},
	});
	map.addLayer({
		id: "value-added-lines",
		type: "line",
		source: "value-added-lines",
		layout: {
			"line-cap": "round",
			"line-join": "round",
		},
		paint: {
			"line-color": ["get", "color"],
			"line-opacity": [
				"case",
				["get", "isSelected"],
				1,
				["get", "opacity"],
			],
			"line-width": [
				"case",
				["get", "isSelected"],
				["+", ["get", "width"], 1.5],
				["get", "width"],
			],
		},
	});
	map.addLayer({
		id: "value-added-points",
		type: "circle",
		source: "value-added-points",
		paint: {
			"circle-color": ["get", "color"],
			"circle-radius": [
				"case",
				["get", "isSelected"],
				["+", ["get", "radius"], 5],
				["get", "radius"],
			],
			"circle-opacity": 0.82,
			"circle-stroke-width": [
				"case",
				["get", "isSelected"],
				2.5,
				1,
			],
			"circle-stroke-color": "#ffffff",
		},
	});
	map.addLayer({
		id: "value-added-point-labels",
		type: "symbol",
		source: "value-added-points",
		layout: {
			"text-field": ["get", "label"],
			"text-size": 12,
			"text-offset": [0, 1.35],
			"text-anchor": "top",
			"text-allow-overlap": false,
		},
		paint: {
			"text-color": "#ffffff",
			"text-halo-color": "#111111",
			"text-halo-width": 1,
		},
	});
	bindLayerInteractions();
}

function updateData() {
	if (!mapReady.value || !map) return;
	map.getSource("value-added-points")?.setData(pointCollection.value);
	map.getSource("value-added-circles")?.setData(circleCollection.value);
	map.getSource("value-added-lines")?.setData(lineCollection.value);
	map.getSource("value-added-districts")?.setData(districtCollection.value);
}

function fitToData() {
	if (!mapReady.value || !map || !hasGeoData.value) return;
	const bounds = new mapboxGl.LngLatBounds();
	districtFeatures.value.forEach((feature) => extendBoundsByGeometry(bounds, feature.geometry));
	pointFeatures.value.forEach((feature) => bounds.extend(feature.geometry.coordinates));
	lineFeatures.value.forEach((feature) => {
		feature.geometry.coordinates.forEach((coordinate) => bounds.extend(coordinate));
	});
	circleFeatures.value.forEach((feature) => {
		feature.geometry.coordinates[0].forEach((coordinate) => bounds.extend(coordinate));
	});
	if (!bounds.isEmpty()) {
		map.fitBounds(bounds, {
			padding: 34,
			duration: 650,
			maxZoom: 12.6,
		});
	}
}

async function fetchDistrictBoundary() {
	try {
		const response = await fetch("/mapData/metrotaipei_town.geojson");
		districtBoundary.value = await response.json();
		updateData();
		fitToData();
	} catch (error) {
		console.error("Failed to load district boundary:", error);
	}
}

function bindLayerInteractions() {
	if (!map) return;
	["value-added-points", "value-added-lines", "value-added-district-fill"].forEach((layerId) => {
		map.on("click", layerId, (event) => {
			const feature = event.features?.[0];
			if (feature?.properties?.label) {
				emit("select", {
					label: feature.properties.label,
					value: Number(feature.properties.value || 0),
				});
			}
		});
		map.on("mouseenter", layerId, () => {
			map.getCanvas().style.cursor = "pointer";
		});
		map.on("mouseleave", layerId, () => {
			map.getCanvas().style.cursor = "";
		});
	});
}

function extendBoundsByGeometry(bounds, geometry) {
	if (!geometry) return;
	if (geometry.type === "Polygon") {
		geometry.coordinates.flat().forEach((coordinate) => bounds.extend(coordinate));
	}
	if (geometry.type === "MultiPolygon") {
		geometry.coordinates.flat(2).forEach((coordinate) => bounds.extend(coordinate));
	}
}

function isValidCoordinate(item) {
	const lat = Number(item?.lat);
	const lng = Number(item?.lng);
	return Number.isFinite(lat) && Number.isFinite(lng);
}

function lineCoordinates(item) {
	if (Array.isArray(item?.coordinates) && item.coordinates.length >= 2) {
		const coordinates = item.coordinates
			.map((coordinate) => Array.isArray(coordinate) ? coordinate.map(Number) : [])
			.filter((coordinate) => coordinate.length >= 2 && Number.isFinite(coordinate[0]) && Number.isFinite(coordinate[1]));
		return coordinates.length >= 2 ? coordinates : null;
	}
	const from = item?.from;
	const to = item?.to;
	if (!isValidCoordinate(from) || !isValidCoordinate(to)) return null;
	return [
		[Number(from.lng), Number(from.lat)],
		[Number(to.lng), Number(to.lat)],
	];
}

function circlePolygon(center, radiusKm, steps = 72) {
	const [lng, lat] = center;
	const coordinates = [];
	const earthRadiusKm = 6371;
	const latRad = toRadians(lat);
	const lngRad = toRadians(lng);
	const angularDistance = radiusKm / earthRadiusKm;

	for (let index = 0; index <= steps; index++) {
		const bearing = toRadians((index / steps) * 360);
		const pointLat = Math.asin(
			Math.sin(latRad) * Math.cos(angularDistance) +
				Math.cos(latRad) * Math.sin(angularDistance) * Math.cos(bearing),
		);
		const pointLng = lngRad + Math.atan2(
			Math.sin(bearing) * Math.sin(angularDistance) * Math.cos(latRad),
			Math.cos(angularDistance) - Math.sin(latRad) * Math.sin(pointLat),
		);
		coordinates.push([toDegrees(pointLng), toDegrees(pointLat)]);
	}

	return {
		type: "Polygon",
		coordinates: [coordinates],
	};
}

function toRadians(value) {
	return value * Math.PI / 180;
}

function toDegrees(value) {
	return value * 180 / Math.PI;
}
</script>

<template>
  <div
    class="value-map"
    :style="{ minHeight: `${height}px` }"
  >
    <div
      v-if="hasMapToken"
      ref="mapEl"
      class="value-map-canvas"
    />
    <div
      v-else
      class="value-map-state"
    >
      Mapbox token 未設定
    </div>
    <div
      v-if="hasMapToken && !hasGeoData"
      class="value-map-state"
    >
      尚無可定位資料
    </div>
  </div>
</template>

<style scoped lang="scss">
.value-map {
  position: relative;
  overflow: hidden;
  border: solid 1px rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(9, 9, 9, 0.24);
}

.value-map-canvas {
  position: absolute;
  inset: 0;
}

.value-map-state {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: var(--color-complement-text);
  background: rgba(9, 9, 9, 0.62);
  font-size: 0.88rem;
  z-index: 1;
}

:deep(.mapboxgl-ctrl-bottom-left),
:deep(.mapboxgl-ctrl-bottom-right) {
  display: none;
}

:deep(.mapboxgl-ctrl-group) {
  background: rgba(20, 20, 20, 0.78);
  border: solid 1px rgba(255, 255, 255, 0.12);
}

:deep(.mapboxgl-ctrl button) {
  filter: invert(1);
}
</style>
