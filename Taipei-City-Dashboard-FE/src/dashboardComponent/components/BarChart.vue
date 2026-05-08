<!-- Developed by Taipei Urban Intelligence Center 2023-2024-->
<script setup>
import { ref, computed } from "vue";
import VueApexCharts from "vue3-apexcharts";

const props = defineProps([
	"chart_config",
	"activeChart",
	"series",
	"map_config",
	"map_filter",
	"map_filter_on",
]);

const emits = defineEmits([
	"filterByParam",
	"filterByLayer",
	"clearByParamFilter",
	"clearByLayerFilter",
	"fly"
]);

const rankedSeries = computed(() => {
	const categories = props.chart_config.categories || [];
	const rankedData = categories.map((category, index) => ({
		x: category,
		y: props.series.reduce((sum, serie) => {
			const value = serie.data[index];
			return sum + Number(value?.y ?? value ?? 0);
		}, 0),
	}));

	rankedData.sort((a, b) => b.y - a.y);
	return [{ name: "優良餐廳", data: rankedData }];
});

const displaySeries = computed(() => (
	props.activeChart === "RankListChart" ? rankedSeries.value : props.series
));

const isNtuMetric = computed(() => props.chart_config.unit === "NTU");
const isAuditViolationMetric = computed(() =>
	["food_audit_violation", "health_audit_violation"].includes(
		props.chart_config.index
	)
);
const auditViolationRangeColors = [
	"#72C6A4",
	"#F2C94C",
	"#F2994A",
	"#E86F51",
	"#B8325A",
];

function getDataPointValue(item) {
	return Number(item?.y ?? item ?? 0);
}

function getDataPointLabel(item, index) {
	return item?.x ?? props.chart_config.categories?.[index] ?? "";
}

function getNtuColor(value) {
	const colors = props.chart_config.color || [];
	if (value < 0.1) return colors[0] || "#2F7D6D";
	if (value <= 0.3) return colors[1] || "#30B68F";
	if (value <= 0.5) return colors[2] || "#1E88E5";
	if (value <= 2) return colors[3] || "#F5B041";
	return colors[4] || "#D84C73";
}

function getAuditViolationColor(value) {
	if (value <= 5) return auditViolationRangeColors[0];
	if (value <= 10) return auditViolationRangeColors[1];
	if (value <= 20) return auditViolationRangeColors[2];
	if (value <= 40) return auditViolationRangeColors[3];
	return auditViolationRangeColors[4];
}

const chartSeries = computed(() => {
	if (!isNtuMetric.value && !isAuditViolationMetric.value) {
		return displaySeries.value;
	}

	return displaySeries.value.map((serie) => ({
		...serie,
		data: serie.data.map((item, index) => {
			const y = getDataPointValue(item);
			const fillColor = isNtuMetric.value
				? getNtuColor(y)
				: getAuditViolationColor(y);
			return {
				...(typeof item === "object" && item !== null ? item : {}),
				x: getDataPointLabel(item, index),
				y,
				fillColor,
			};
		}),
	}));
});

const chartOptions = ref({
	chart: {
		offsetY: 15,
		stacked: true,
		toolbar: {
			show: false,
		},
	},
	colors: [...props.chart_config.color],
	dataLabels: {
		offsetX: 20,
		textAnchor: "start",
	},
	grid: {
		show: false,
	},
	legend: {
		show: false,
	},
	plotOptions: {
		bar: {
			borderRadius: 2,
			distributed: true,
			horizontal: true,
			dataLabels: {
				hideOverflowingLabels: false
			},
		},
	},
	stroke: {
		colors: ["#282a2c"],
		show: true,
		width: 0,
	},
	// The class "chart-tooltip" could be edited in /assets/styles/chartStyles.css
	tooltip: {
		custom: function ({
			series,
			seriesIndex,
			dataPointIndex,
			w,
		}) {
			return (
				'<div class="chart-tooltip">' +
				"<h6>" +
				w.globals.labels[dataPointIndex] +
				"</h6>" +
				"<span>" +
				series[seriesIndex][dataPointIndex] +
				` ${props.chart_config.unit}` +
				"</span>" +
				"</div>"
			);
		},
		followCursor: true,
	},
	xaxis: {
		axisBorder: {
			show: false,
		},
		axisTicks: {
			show: false,
		},
		labels: {
			show: false,
		},
		categories: props.chart_config.categories
			? props.chart_config.categories
			: [],
		type: "category",
	},
	yaxis: {
		labels: {
			formatter: function (value) {
				return value.length > 7 ? value.slice(0, 6) + "..." : value;
			},
		},
	},
});

const chartHeight = computed(() => {
	return `${40 + chartSeries.value[0].data.length * 30}`;
});

const selectedIndex = ref(null);

function handleDataSelection(_e, _chartContext, config) {
	if (!props.map_filter || !props.map_filter_on) {
		return;
	}
	if (
		`${config.dataPointIndex}-${config.seriesIndex}` !== selectedIndex.value
	) {
		// Supports filtering by xAxis
		if (props.map_filter.mode === "byParam") {
			emits(
				"filterByParam",
				props.map_filter,
				props.map_config,
				config.w.globals.labels[config.dataPointIndex],
				null
			);
		}
		// Supports filtering by xAxis
		else if (props.map_filter.mode === "byLayer") {
			emits(
				"filterByLayer",
				props.map_config,
				config.w.globals.labels[config.dataPointIndex]
			);
		}
		selectedIndex.value = `${config.dataPointIndex}-${config.seriesIndex}`;
	} else {
		if (props.map_filter.mode === "byParam") {
			emits("clearByParamFilter", props.map_config);
		} else if (props.map_filter.mode === "byLayer") {
			emits("clearByLayerFilter", props.map_config);
		}
		selectedIndex.value = null;
	}
}
</script>

<template>
  <div v-if="activeChart === 'BarChart' || activeChart === 'RankListChart'">
    <VueApexCharts
      width="100%"
      :height="chartHeight"
      type="bar"
      :options="chartOptions"
      :series="chartSeries"
      @data-point-selection="handleDataSelection"
    />
  </div>
</template>
