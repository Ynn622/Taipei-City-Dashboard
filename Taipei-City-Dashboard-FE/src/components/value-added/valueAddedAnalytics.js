export const COMPONENT_IDS = {
	goodRestaurants: 501,
	market: 303,
	infectious: 502,
	waterQuality: 306,
	healthOffice: 305,
	foodSource: 307,
	foodAuditViolation: 308,
	healthAuditViolation: 309,
	postHelpAgency: 310,
};

export const GEOJSON_FILES = {
	foodSource: ["food_source_tpe.geojson", "food_source_ntpe.geojson"],
	market: ["food_safety_market_tpe.geojson", "food_safety_market_ntpe.geojson"],
	waterQuality: ["water_quality_tpe.geojson", "water_quality_ntpe.geojson"],
	healthOffice: [
		"food_safety_health_office_tpe.geojson",
		"food_safety_health_office_ntpe.geojson",
	],
	healthAudit: [
		"health_audit_violation_tpe.geojson",
		"health_audit_violation_ntpe.geojson",
	],
	foodAudit: [
		"food_audit_violation_tpe.geojson",
		"food_audit_violation_ntpe.geojson",
	],
	postHelp: ["post_help_agency_tpe.geojson", "post_help_agency_ntpe.geojson"],
	goodRestaurants: ["fda_good_restaurants.geojson"],
};

export const COMPONENT_GEOJSON_FALLBACKS = {
	[COMPONENT_IDS.goodRestaurants]: {
		files: GEOJSON_FILES.goodRestaurants,
		groupKey: "district",
	},
	[COMPONENT_IDS.market]: {
		files: GEOJSON_FILES.market,
		groupKey: "district",
		valueKey: "stall_total",
	},
	[COMPONENT_IDS.waterQuality]: {
		files: GEOJSON_FILES.waterQuality,
		groupKey: "district",
	},
	[COMPONENT_IDS.healthOffice]: {
		files: GEOJSON_FILES.healthOffice,
		groupKey: "district",
	},
	[COMPONENT_IDS.foodSource]: {
		files: GEOJSON_FILES.foodSource,
		groupKey: "district",
	},
	[COMPONENT_IDS.foodAuditViolation]: {
		files: GEOJSON_FILES.foodAudit,
		groupKey: "district",
	},
	[COMPONENT_IDS.healthAuditViolation]: {
		files: GEOJSON_FILES.healthAudit,
		groupKey: "district",
	},
	[COMPONENT_IDS.postHelpAgency]: {
		files: GEOJSON_FILES.postHelp,
		groupKey: "agency_type",
	},
};

export function unwrapRows(payload) {
	if (!payload) return [];
	if (Array.isArray(payload.categories) && Array.isArray(payload.data)) {
		const categoryRows = rowsFromCategorySeries(payload);
		if (categoryRows.length > 0) return categoryRows;
	}
	if (Array.isArray(payload)) return flattenChartRows(payload);
	if (Array.isArray(payload.data)) return flattenChartRows(payload.data);
	if (Array.isArray(payload.rows)) return flattenChartRows(payload.rows);
	if (payload.data && Array.isArray(payload.data.data)) return flattenChartRows(payload.data.data);
	return [];
}

function rowsFromCategorySeries(payload) {
	const seriesList = payload.data.filter((series) => Array.isArray(series?.data));
	if (seriesList.length === 0) return [];
	return payload.categories.map((label, index) => {
		const data = seriesList.reduce((sum, series) => {
			const value = Number(series.data[index] ?? 0);
			return sum + (Number.isFinite(value) ? value : 0);
		}, 0);
		return { x_axis: label, data };
	});
}

function flattenChartRows(rows) {
	if (!Array.isArray(rows)) return [];
	if (
		rows.some((row) => Array.isArray(row?.data)) &&
		rows.some((row) => Array.isArray(row?.data) && row.data.some((item) => isRowObject(item)))
	) {
		return rows.flatMap((row) => row.data.filter((item) => isRowObject(item)));
	}
	return rows;
}

function isRowObject(item) {
	return item && typeof item === "object" && !Array.isArray(item);
}

export function rowLabel(row) {
	return (
		row?.x_axis ||
		row?.x ||
		row?.name ||
		row?.district ||
		row?.agency_type ||
		row?.rating_result ||
		"未分類"
	);
}

export function rowGroup(row) {
	return row?.y_axis || row?.category || row?.type || "";
}

export function rowValue(row) {
	const value = Number(
		row?.data ??
			row?.y ??
			row?.value ??
			row?.count ??
			row?.total ??
			row?.violation_count ??
			0
	);
	return Number.isFinite(value) ? value : 0;
}

export function sumRows(rows) {
	return unwrapRows(rows).reduce((sum, row) => sum + rowValue(row), 0);
}

export function formatNumber(value, unit = "") {
	const number = Number(value);
	if (!Number.isFinite(number)) return `0${unit}`;
	return `${Math.round(number).toLocaleString("zh-TW")}${unit}`;
}

export function formatDelta(value, unit = "") {
	const number = Number(value);
	if (!Number.isFinite(number)) return "無法比較";
	if (number === 0) return `持平 ${formatNumber(0, unit)}`;
	return `${number > 0 ? "增加" : "減少"} ${formatNumber(Math.abs(number), unit)}`;
}

export function topRows(rows, limit = 5) {
	return aggregateByLabel(rows)
		.sort((a, b) => b.value - a.value)
		.slice(0, limit);
}

export function aggregateByLabel(rows) {
	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = rowLabel(row);
		totals.set(label, (totals.get(label) || 0) + rowValue(row));
	});
	return [...totals.entries()].map(([label, value]) => ({ label, value }));
}

export function aggregateByGroup(rows) {
	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = rowGroup(row) || rowLabel(row);
		totals.set(label, (totals.get(label) || 0) + rowValue(row));
	});
	return [...totals.entries()]
		.map(([label, value]) => ({ label, value }))
		.sort((a, b) => b.value - a.value);
}

export function profileDistricts(profile) {
	return Array.isArray(profile?.focusDistricts)
		? profile.focusDistricts.filter(Boolean)
		: [];
}

export function profileCategories(profile) {
	return Array.isArray(profile?.focusCategories)
		? profile.focusCategories.filter(Boolean)
		: [];
}

export function filterByProfileDistrict(rows, profile) {
	const districts = profileDistricts(profile);
	if (districts.length === 0) return unwrapRows(rows);
	return unwrapRows(rows).filter((row) => districts.includes(rowLabel(row)));
}

export function trendSummary(rows) {
	const points = getTrendPoints(rows);
	if (points.length === 0) {
		return {
			latest: null,
			previous: null,
			delta: null,
			direction: "無資料",
			hasData: false,
		};
	}
	if (points.length < 2) {
		return {
			latest: points[0]?.value || 0,
			previous: null,
			delta: null,
			direction: "資料不足",
			hasData: true,
		};
	}
	const latest = points[points.length - 1].value;
	const previous = points[points.length - 2].value;
	const delta = latest - previous;
	return {
		latest,
		previous,
		delta,
		direction: delta > 0 ? "上升" : delta < 0 ? "下降" : "持平",
		hasData: true,
	};
}

export function metricComparison(payload, options = {}) {
	const unit = options.unit || "";
	const mode = options.mode || "count";
	const emptyText = options.emptyText || "無資料";
	if (options.static) {
		const rawRows = rawRowsForComparison(payload);
		if (rawRows.length === 0) {
			return emptyComparison(emptyText);
		}
		const current = mode === "length" ? rawRows.length : sumRows(payload);
		return {
			current,
			previous: null,
			delta: null,
			hasData: true,
			canCompare: false,
			currentLabelText: "名冊",
			previousLabelText: "比較",
			currentText: formatNumber(current, unit),
			previousText: "靜態名冊",
			deltaText: "無法比較",
		};
	}

	const trend = getTimeSeriesPoints(payload, options);

	if (trend.length >= 2) {
		const previous = trend[trend.length - 2].value;
		const current = trend[trend.length - 1].value;
		return {
			current,
			previous,
			delta: current - previous,
			currentLabel: trend[trend.length - 1].label,
			previousLabel: trend[trend.length - 2].label,
			hasData: true,
			canCompare: true,
			currentLabelText: "最新週",
			previousLabelText: "前一週",
			currentText: formatNumber(current, unit),
			previousText: formatNumber(previous, unit),
			deltaText: formatDelta(current - previous, unit),
		};
	}

	const rawRows = rawRowsForComparison(payload);
	if (rawRows.length === 0) {
		return emptyComparison(emptyText);
	}
	const datedRows = rawRows
		.map((row) => ({ row, date: parseMetricDate(row) }))
		.filter((item) => item.date);

	if (datedRows.length === 0) {
		const current = mode === "length" ? rawRows.length : sumRows(payload);
		return {
			current,
			previous: null,
			delta: null,
			hasData: true,
			canCompare: false,
			currentLabelText: "總計",
			previousLabelText: "比較",
			currentText: formatNumber(current, unit),
			previousText: "無分週資料",
			deltaText: "無法比較",
		};
	}

	const latestTime = Math.max(...datedRows.map((item) => item.date.getTime()));
	const currentEnd = endOfDay(new Date(latestTime));
	const currentStart = addDays(currentEnd, -6);
	const previousEnd = addDays(currentStart, -1);
	const previousStart = addDays(previousEnd, -6);

	const currentRows = datedRows
		.filter((item) => item.date >= currentStart && item.date <= currentEnd)
		.map((item) => item.row);
	const previousRows = datedRows
		.filter((item) => item.date >= previousStart && item.date <= previousEnd)
		.map((item) => item.row);
	const current = metricRowsValue(currentRows, mode);
	const previous = metricRowsValue(previousRows, mode);

	return {
		current,
		previous,
		delta: current - previous,
		currentLabel: `${formatDate(currentStart)}-${formatDate(currentEnd)}`,
		previousLabel: `${formatDate(previousStart)}-${formatDate(previousEnd)}`,
		hasData: true,
		canCompare: true,
		currentLabelText: "最新週",
		previousLabelText: "前一週",
		currentText: formatNumber(current, unit),
		previousText: formatNumber(previous, unit),
		deltaText: formatDelta(current - previous, unit),
	};
}

export function highRiskAreaComparison(rows, options = {}) {
	const threshold = typeof options === "number" ? options : options.threshold || 1;
	const groupKey = typeof options === "object" ? options.groupKey : "";
	const rawRows = rawRowsForComparison(rows);
	if (rawRows.length === 0) {
		return emptyComparison("無資料");
	}
	const datedRows = rawRows
		.map((row) => ({ row, date: parseMetricDate(row) }))
		.filter((item) => item.date);

	if (datedRows.length === 0) {
		const current = aggregateRowsByMetricLabel(rawRows, groupKey)
			.filter((item) => item.value >= threshold).length;
		return {
			current,
			previous: null,
			delta: null,
			hasData: true,
			canCompare: false,
			currentLabelText: "總計",
			previousLabelText: "比較",
			currentText: formatNumber(current, " 區"),
			previousText: "無分週資料",
			deltaText: "無法比較",
		};
	}

	const latestTime = Math.max(...datedRows.map((item) => item.date.getTime()));
	const currentEnd = endOfDay(new Date(latestTime));
	const currentStart = addDays(currentEnd, -6);
	const previousEnd = addDays(currentStart, -1);
	const previousStart = addDays(previousEnd, -6);
	const current = countHighRiskAreas(datedRows, currentStart, currentEnd, threshold, groupKey);
	const previous = countHighRiskAreas(datedRows, previousStart, previousEnd, threshold, groupKey);

	return {
		current,
		previous,
		delta: current - previous,
		hasData: true,
		canCompare: true,
		currentLabelText: "最新週",
		previousLabelText: "前一週",
		currentText: formatNumber(current, " 區"),
		previousText: formatNumber(previous, " 區"),
		deltaText: formatDelta(current - previous, " 區"),
	};
}

export function aggregateByX(rows) {
	return getTrendPoints(rows);
}

function getTrendPoints(rows) {
	return trendPoints(rows);
}

function trendPoints(rows, options = {}) {
	if (
		Array.isArray(rows?.categories) &&
		Array.isArray(rows?.data) &&
		rows.data.some((series) => Array.isArray(series?.data))
	) {
		const seriesList = rows.data.filter((series) => shouldIncludeSeries(series, options));
		return rows.categories.map((label, index) => {
			const value = seriesList.reduce((sum, series) => {
				const point = Number(series?.data?.[index] ?? 0);
				return sum + (Number.isFinite(point) ? point : 0);
			}, 0);
			return { label, value };
		});
	}

	if (
		Array.isArray(rows?.data) &&
		rows.data.some((series) => Array.isArray(series?.data) && series.data.some((point) => point?.x))
	) {
		const totals = new Map();
		rows.data
			.filter((series) => shouldIncludeSeries(series, options))
			.forEach((series) => {
				series.data.forEach((point) => {
					const label = point?.x;
					const value = Number(point?.y ?? 0);
					if (!label || !Number.isFinite(value)) return;
					totals.set(label, (totals.get(label) || 0) + value);
				});
			});
		return [...totals.entries()].map(([label, value]) => ({ label, value }));
	}

	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = rowLabel(row);
		totals.set(label, (totals.get(label) || 0) + rowValue(row));
	});
	return [...totals.entries()].map(([label, value]) => ({ label, value }));
}

function getTimeSeriesPoints(payload, options = {}) {
	if (
		Array.isArray(payload?.categories) &&
		Array.isArray(payload?.data) &&
		payload.data.some((series) => Array.isArray(series?.data))
	) {
		return trendPoints(payload, options);
	}

	if (
		Array.isArray(payload?.data) &&
		payload.data.some((series) => Array.isArray(series?.data) && series.data.some((point) => point?.x))
	) {
		return trendPoints(payload, options);
	}

	const rows = unwrapRows(payload);
	if (!rows.some((row) => parseMetricDate({ x_axis: row?.x_axis }))) {
		return [];
	}
	return trendPoints(payload, options);
}

function rawRowsForComparison(payload) {
	if (Array.isArray(payload?.rawRows)) return payload.rawRows;
	return unwrapRows(payload);
}

function emptyComparison(text) {
	return {
		current: null,
		previous: null,
		delta: null,
		hasData: false,
		canCompare: false,
		currentLabelText: "狀態",
		previousLabelText: "比較",
		currentText: text,
		previousText: "未取得資料",
		deltaText: "無法比較",
	};
}

function shouldIncludeSeries(series, options = {}) {
	if (Array.isArray(options.seriesNames) && options.seriesNames.length > 0) {
		return options.seriesNames.includes(series?.name);
	}
	if (Array.isArray(options.excludeSeriesNames) && options.excludeSeriesNames.length > 0) {
		return !options.excludeSeriesNames.includes(series?.name);
	}
	return true;
}

function metricRowsValue(rows, mode) {
	if (mode === "length") return rows.length;
	return rows.reduce((sum, row) => sum + rowValue(row), 0);
}

function countHighRiskAreas(datedRows, start, end, threshold, groupKey = "") {
	const totals = new Map();
	datedRows.forEach((item) => {
		if (item.date < start || item.date > end) return;
		const label = metricLabel(item.row, groupKey);
		totals.set(label, (totals.get(label) || 0) + rowValue(item.row));
	});
	return [...totals.values()].filter((value) => value >= threshold).length;
}

function aggregateRowsByMetricLabel(rows, groupKey = "") {
	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = metricLabel(row, groupKey);
		totals.set(label, (totals.get(label) || 0) + rowValue(row));
	});
	return [...totals.entries()].map(([label, value]) => ({ label, value }));
}

function metricLabel(row, groupKey = "") {
	return (groupKey && row?.[groupKey]) || rowLabel(row);
}

function parseMetricDate(row) {
	const raw =
		row?.data_time ||
		row?.audit_date ||
		row?.sample_date ||
		row?.date ||
		row?.x_axis;
	if (!raw) return null;

	const normalized = String(raw).trim().replace(/\./g, "-").replace(/\//g, "-");
	const match = normalized.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
	if (!match) return null;
	const date = new Date(
		Number(match[1]),
		Number(match[2]) - 1,
		Number(match[3])
	);
	return Number.isNaN(date.getTime()) ? null : date;
}

function endOfDay(date) {
	const next = new Date(date);
	next.setHours(23, 59, 59, 999);
	return next;
}

function addDays(date, days) {
	const next = new Date(date);
	next.setDate(next.getDate() + days);
	return next;
}

function formatDate(date) {
	return `${date.getMonth() + 1}/${date.getDate()}`;
}

export function geoJsonFeatures(collections) {
	return collections.flatMap((collection) => collection?.features || []);
}

export function featureProps(feature) {
	return feature?.properties || {};
}

export function buildFallbackChartData(componentId, collections) {
	const config = COMPONENT_GEOJSON_FALLBACKS[componentId];
	if (!config) return null;

	const totals = new Map();
	geoJsonFeatures(collections).forEach((feature) => {
		const props = featureProps(feature);
		const label = props[config.groupKey] || props.district || props.city || "未分類";
		const rawValue = config.valueKey ? Number(props[config.valueKey]) : 1;
		const value = Number.isFinite(rawValue) && rawValue > 0 ? rawValue : 1;
		totals.set(label, (totals.get(label) || 0) + value);
	});

	const data = [...totals.entries()]
		.map(([x_axis, data]) => ({ x_axis, data: Math.round(data) }))
		.sort((a, b) => b.data - a.data);

	return {
		status: "success",
		data,
		rawRows: geoJsonFeatures(collections).map((feature) => featureProps(feature)),
		fallback: true,
	};
}

export function topFeatures(features, getLabel, getValue, limit = 5) {
	return [...features]
		.map((feature) => ({
			label: getLabel(featureProps(feature)),
			value: Number(getValue(featureProps(feature)) || 0),
			props: featureProps(feature),
		}))
		.filter((item) => item.label)
		.sort((a, b) => b.value - a.value)
		.slice(0, limit);
}

export function maxValue(items) {
	return Math.max(...items.map((item) => item.value), 1);
}

export function localSuggestion(feature, profile, context = {}) {
	const name = profile?.name ? `${profile.name}，` : "";
	const districts = profileDistricts(profile).join("、") || "目前關注區域";
	const categories = profileCategories(profile).join("、") || "主要食安類型";
	const top = context.topItems?.[0]?.label || context.hotspot || "高風險項目";
	return `${name}建議先把 ${districts} 的 ${categories} 納入本週追蹤，優先處理「${top}」。可搭配稽查違規、供應來源與就診趨勢三類資料交叉確認，再安排現場查核或替代供應方案。`;
}
