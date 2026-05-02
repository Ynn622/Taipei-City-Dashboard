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

const treemapSeries = computed(() => {
	if (!props.chart_config.categories) {
		return props.series;
	}

	const data = props.chart_config.categories.map((category, index) => ({
		x: category,
		y: props.series.reduce((sum, serie) => {
			const value = serie.data[index];
			return sum + Number(value?.y ?? value ?? 0);
		}, 0),
	}));

	data.sort((a, b) => b.y - a.y);
	return [{ name: "優良餐廳", data }];
});

const chartOptions = ref({
	chart: {
		borderRadius: 5,
		toolbar: {
			show: false,
		},
	},
	colors: [...props.chart_config.color],
	dataLabels: {
		formatter: function (
			val,
			{ dataPointIndex }
		) {
			return dataPointIndex > 5 ? "" : val;
		},
	},
	grid: {
		show: false,
	},
	legend: {
		show: false,
	},
	plotOptions: {
		treemap: {
			distributed: true,
			shadeIntensity: 0,
		},
	},
	stroke: {
		colors: ["#282a2c"],
		show: true,
		width: 2,
	},
	tooltip: {
		custom: function ({
			series,
			seriesIndex,
			dataPointIndex,
			w,
		}) {
			// The class "chart-tooltip" could be edited in /assets/styles/chartStyles.css
			return (
				'<div class="chart-tooltip">' +
				"<h6>" +
				w.globals.categoryLabels[dataPointIndex] +
				"</h6>" +
				"<span>" +
				series[seriesIndex][dataPointIndex] +
				` ${props.chart_config.unit}` +
				"</span>" +
				"</div>"
			);
		},
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
		type: "category",
	},
});

const sum = computed(() => {
	let sum = 0;
	treemapSeries.value[0].data.forEach(
		(item) => (sum += Number(item.y ?? item ?? 0))
	);
	return Math.round(sum * 100) / 100;
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
				config.w.globals.categoryLabels[config.dataPointIndex],
				null
			);
		}
		// Supports filtering by xAxis
		else if (props.map_filter.mode === "byLayer") {
			emits(
				"filterByLayer",
				props.map_config,
				config.w.globals.categoryLabels[config.dataPointIndex]
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
  <div
    v-if="activeChart === 'TreemapChart'"
    class="treemapchart"
  >
    <div class="treemapchart-title">
      <h5>總合</h5>
      <h6>{{ sum }} {{ chart_config.unit }}</h6>
    </div>
    <VueApexCharts
      width="100%"
      type="treemap"
      :options="chartOptions"
      :series="treemapSeries"
      @data-point-selection="handleDataSelection"
    />
  </div>
</template>

<style scoped lang="scss">
.treemapchart {
	&-title {
		display: flex;
		justify-content: center;
		flex-direction: column;
		margin: 0.5rem 0 -0.5rem;

		h5 {
			margin: 0;
			color: var(--color-complement-text);
		}

		h6 {
			margin: 0;
			color: var(--color-complement-text);
			font-size: var(--font-m);
			font-weight: 400;
		}
	}
}
</style>
