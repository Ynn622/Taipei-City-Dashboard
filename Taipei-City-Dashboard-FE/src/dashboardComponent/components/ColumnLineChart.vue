<!-- Developed by Open Possible (台灣大哥大), Taipei Codefest 2023 -->
<!-- Refactored and Maintained by Taipei Urban Intelligence Center -->

<script setup>
import { ref, computed, watch } from "vue";
import VueApexCharts from "vue3-apexcharts";

const props = defineProps(["chart_config", "activeChart", "series"]);

// const emits = defineEmits([
// 	"filterByParam",
// 	"filterByLayer",
// 	"clearByParamFilter",
// 	"clearByLayerFilter",
// 	"fly"
// ]);

// 原始資料拷貝避免更改原始資料
const localSeries = ref(JSON.parse(JSON.stringify(props.series || [])));

function isRateSeriesName(name = "") {
	return name.includes("率") || name.includes("%") || name.includes("百分比");
}

function getSeriesUnit(name = "") {
	return isRateSeriesName(name) ? "%" : props.chart_config.unit;
}

function formatValue(value, unit) {
	const number = Number(value);
	if (!Number.isFinite(number)) return value;
	if (unit === "%") return number.toFixed(1);
	if (number !== 0 && Math.abs(number) < 10) return number.toFixed(1);
	return number.toFixed(0);
}

const parseSeries = computed(() => {
	return localSeries.value.map(
		(serie) => ({
			...serie,
			type: isRateSeriesName(serie.name) ? "line" : "column",
		})
	);
});

const firstRateSeriesName = computed(() =>
	localSeries.value.find((serie) => isRateSeriesName(serie.name))?.name ?? ""
);

const totalMax = computed(() => {
	const stackedTotals = new Map();

	localSeries.value
		.filter((serie) => !isRateSeriesName(serie.name))
		.forEach((serie) => {
			serie.data.forEach((d) => {
				const key = d.x;
				stackedTotals.set(key, (stackedTotals.get(key) || 0) + Number(d.y || 0));
			});
		});

	if (stackedTotals.size === 0) return null;

	const max = Math.max(...stackedTotals.values());

	// add 10% then round up to the nearest 100
	return Math.ceil((max * 1.1) / 10) * 10;
});

const xaxisType = ref("datetime");
const tickAmount = ref(undefined);

const countYAxis = computed(() => ({
	min: 0,
	max: function (max) {
		if (totalMax.value) {
			return totalMax.value;
		}
		return max;
	},
	labels: {
		formatter: function (val) {
			return formatValue(val, props.chart_config.unit);
		},
	},
	title: {
		text: props.chart_config.unit,
		style: {
			color: "var(--color-complement-text)",
		},
	},
}));

const rateYAxis = computed(() => ({
	min: 0,
	labels: {
		formatter: function (val) {
			return `${val.toFixed(1)}%`;
		},
	},
	opposite: true,
	title: {
		text: firstRateSeriesName.value,
		style: {
			color: "var(--color-complement-text)",
		},
	},
}));

const chartYAxes = computed(() => {
	const axes = localSeries.value.map((serie, index) => {
		if (isRateSeriesName(serie.name)) {
			return {
				...rateYAxis.value,
				seriesName: serie.name,
			};
		}

		return {
			...countYAxis.value,
			seriesName: serie.name,
			show: index === 0,
			showAlways: index === 0,
		};
	});

	return axes.length > 0 ? axes : [countYAxis.value];
});

const chartOptions = computed(() => ({
	chart: {
		stacked: true,
		stackOnlyBar: true,
		toolbar: {
			show: false,
			tools: {
				zoom: false,
			},
		},
	},
	colors: [...props.chart_config.color],
	dataLabels: {
		enabled: false,
	},
	grid: {
		show: false,
	},
	legend: {
		show: true,
		markers: {
			radius: [0, 20],
		},
	},
	markers: {
		hover: {
			size: 4,
		},
		shape: "circle",
		size: 4,
		strokeWidth: 0,
	},
	stroke: {
		colors: [...props.chart_config.color],
		curve: "smooth",
		show: true,
		width: parseSeries.value.map((serie) => serie.type === "line" ? 2 : 0),
	},
	plotOptions: {
		bar: {
			columnWidth: "55%",
		},
	},
	tooltip: {
		// The class "chart-tooltip" could be edited in /assets/styles/chartStyles.css
		custom: function ({
			series,
			seriesIndex,
			dataPointIndex,
			w,
		}) {
			return (
				`<div class="chart-tooltip">` +
				`<h6>` +
				`${parseTime(w.config.series[0].data[dataPointIndex].x)} - ${
					w.globals.seriesNames[seriesIndex]
				}` +
				`</h6>` +
				`<span>${formatValue(series[seriesIndex][dataPointIndex], getSeriesUnit(w.globals.seriesNames[seriesIndex]))} ${getSeriesUnit(w.globals.seriesNames[seriesIndex])}</span>` +
				`</div>`
			);
		},
		enabled: true,
		followCursor: true,
		intersect: true,
		shared: false,
	},
	xaxis: {
		axisBorder: {
			color: "#555",
			height: "0.8",
		},
		axisTicks: {
			show: false,
		},
		crosshairs: {
			show: false,
			stroke: {
				color: "var(--color-complement-text)",
			},
		},
		labels: {
			datetimeUTC: false,
		},
		tooltip: {
			enabled: false,
		},
		type: xaxisType.value,
		tickAmount: tickAmount.value,
	},
	yaxis: chartYAxes.value,
}));

function parseTime(time) {
	return String(time).replace("T00:00:00+08:00", " ");
}

watch(
	() => props.series,
	(newVal) => {
		localSeries.value = JSON.parse(JSON.stringify(newVal || []));

		const timestamps = newVal?.[0]?.data?.map((p) => new Date(p.x).getTime()) || [];
		if (timestamps.length < 2) return;

		const newDiff = Math.max(...timestamps) - Math.min(...timestamps);

		// 跨度超過三年改成年份類別
		if (newDiff >= 3 * 31536000000) {
			localSeries.value.forEach((item) => {
				item.data = item.data.map((a) => ({
					...a,
					x: a.x.slice(0, 4),
				}));
			});
			xaxisType.value = "category";
			tickAmount.value = Math.floor(newDiff / 31536000000);
		} else {
			xaxisType.value = "datetime";
			tickAmount.value = undefined;
		}
	},
	{ deep: true, immediate: true }
);

</script>

<template>
  <div
    v-if="activeChart === 'ColumnLineChart'"
  >
    <VueApexCharts
      type="line"
      width="100%"
      height="260px"
      :options="chartOptions"
      :series="parseSeries"
    />
  </div>
</template>
