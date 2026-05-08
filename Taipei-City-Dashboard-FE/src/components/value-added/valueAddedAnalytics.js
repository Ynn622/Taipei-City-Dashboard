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
	logisticsVendor: [
		"food_safety_logistics_vendor_tpe.geojson",
		"food_safety_logistics_vendor_ntpe.geojson",
	],
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
	const xAxis = row?.x_axis;
	const xAxisIsDate = xAxis && /^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}/.test(String(xAxis));

	const candidates = xAxisIsDate
		? [row?.name, row?.district, row?.agency_type, row?.rating_result, row?.x, xAxis]
		: [xAxis, row?.x, row?.name, row?.district, row?.agency_type, row?.rating_result];

	for (const candidate of candidates) {
		if (candidate === null || candidate === undefined) continue;
		const str = String(candidate).trim();
		if (str) return str;
	}

	return "未分類";
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

export function normalizeLatLng(value) {
	if (!value) return null;
	if (Array.isArray(value) && value.length >= 2) {
		const [lat, lng] = value.map(Number);
		return validLatLng(lat, lng) ? { lat, lng } : null;
	}
	if (typeof value === "object") {
		const lat = Number(value.lat ?? value.latitude ?? value.y);
		const lng = Number(value.lng ?? value.lon ?? value.longitude ?? value.x);
		return validLatLng(lat, lng) ? { lat, lng } : null;
	}
	if (typeof value === "string") {
		const parts = value.split(/[,，\s]+/).map(Number).filter((item) => Number.isFinite(item));
		if (parts.length >= 2) {
			const [lat, lng] = parts;
			return validLatLng(lat, lng) ? { lat, lng } : null;
		}
	}
	return null;
}

function validLatLng(lat, lng) {
	return Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180;
}

export function haversineKm(from, to) {
	const origin = normalizeLatLng(from);
	const target = normalizeLatLng(to);
	if (!origin || !target) return null;
	const radius = 6371;
	const latDelta = toRadians(target.lat - origin.lat);
	const lngDelta = toRadians(target.lng - origin.lng);
	const a =
		Math.sin(latDelta / 2) ** 2 +
		Math.cos(toRadians(origin.lat)) *
			Math.cos(toRadians(target.lat)) *
			Math.sin(lngDelta / 2) ** 2;
	return radius * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function toRadians(value) {
	return value * Math.PI / 180;
}

export function rowLatLng(row) {
	const direct = normalizeLatLng(row);
	if (direct) return direct;
	const geometry = row?.geometry || row?._geometry;
	if (Array.isArray(geometry?.coordinates)) {
		const [lng, lat] = geometry.coordinates;
		return normalizeLatLng({ lat, lng });
	}
	const district = row?.district || rowLabel(row);
	return DISTRICT_COORDS[district] || null;
}

export function sortByDistanceThenDistrict(rows, userLocation, options = {}) {
	const origin = normalizeLatLng(userLocation) || districtLocation(options.fallbackDistricts?.[0]);
	return unwrapRows(rows)
		.map((row) => {
			const label = rowLabel(row);
			const distance = origin ? haversineKm(origin, rowLatLng(row) || DISTRICT_COORDS[label]) : null;
			return {
				label,
				value: rowValue(row),
				distance,
				distanceText: distance === null ? "距離待補" : `${distance.toFixed(1)} km`,
				row,
			};
		})
		.sort((a, b) => {
			if (a.distance !== null && b.distance !== null && a.distance !== b.distance) {
				return a.distance - b.distance;
			}
			if (a.distance !== null && b.distance === null) return -1;
			if (a.distance === null && b.distance !== null) return 1;
			return a.label.localeCompare(b.label, "zh-Hant");
		});
}

export function districtLocation(district) {
	return DISTRICT_COORDS[district] || null;
}

export function parseYmdRange(text) {
	if (!text) return null;
	const [from, to] = String(text).split("-").map((item) => parseYmd(item));
	if (!from || !to) return null;
	const start = from <= to ? from : to;
	const end = endOfDay(from <= to ? to : from);
	return { start, end };
}

function parseYmd(value) {
	const raw = String(value || "").trim();
	const compact = raw.match(/^(\d{4})(\d{2})(\d{2})$/);
	const dashed = raw.replace(/\//g, "-").match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
	const match = compact || dashed;
	if (!match) return null;
	const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
	return Number.isNaN(date.getTime()) ? null : date;
}

export function filterRowsByDateRange(rows, rangeText) {
	const range = parseYmdRange(rangeText);
	const source = unwrapRows(rows);
	if (!range) return source;
	const dated = source.filter((row) => {
		const date = parseMetricDate(row);
		return date && date >= range.start && date <= range.end;
	});
	return dated.length > 0 ? dated : source;
}

export function rankRows(rows, options = {}) {
	const limit = options.limit || 6;
	const groupKey = options.groupKey || "";
	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = (groupKey && row?.[groupKey]) || row?.product_category || row?.business_category || rowGroup(row) || rowLabel(row);
		totals.set(label, (totals.get(label) || 0) + rowValue(row));
	});
	return [...totals.entries()]
		.map(([label, value]) => ({ label, value }))
		.sort((a, b) => b.value - a.value)
		.slice(0, limit)
		.map((item, index) => ({ ...item, rank: index + 1 }));
}

export function computePeriodDelta(rows, options = {}) {
	const groupKey = options.groupKey || "";
	const source = unwrapRows(rows);
	const datedRows = source
		.map((row) => ({ row, date: parseMetricDate(row) }))
		.filter((item) => item.date);
	if (datedRows.length === 0) {
		return rankRows(source, { groupKey, limit: options.limit || 6 })
			.map((item) => ({ ...item, current: item.value, previous: 0, delta: item.value, deltaRate: null }));
	}
	const latest = endOfDay(new Date(Math.max(...datedRows.map((item) => item.date.getTime()))));
	const days = options.days || 30;
	const currentStart = addDays(latest, -(days - 1));
	const previousEnd = addDays(currentStart, -1);
	const previousStart = addDays(previousEnd, -(days - 1));
	return rankByDelta(source, {
		groupKey,
		limit: options.limit || 6,
		currentStart,
		currentEnd: latest,
		previousStart,
		previousEnd,
	});
}

export function rankByDelta(rows, options = {}) {
	const groupKey = options.groupKey || "";
	const totals = new Map();
	unwrapRows(rows).forEach((row) => {
		const label = (groupKey && row?.[groupKey]) || row?.product_category || row?.business_category || rowGroup(row) || rowLabel(row);
		const bucket = totals.get(label) || { label, current: 0, previous: 0 };
		const date = parseMetricDate(row);
		if (date && options.currentStart && date >= options.currentStart && date <= options.currentEnd) {
			bucket.current += rowValue(row);
		} else if (date && options.previousStart && date >= options.previousStart && date <= options.previousEnd) {
			bucket.previous += rowValue(row);
		} else if (!date) {
			bucket.current += rowValue(row);
		}
		totals.set(label, bucket);
	});
	return [...totals.values()]
		.map((item) => ({
			...item,
			value: item.current,
			delta: item.current - item.previous,
			deltaRate: item.previous > 0 ? (item.current - item.previous) / item.previous : null,
		}))
		.sort((a, b) => b.delta - a.delta || b.current - a.current)
		.slice(0, options.limit || 6)
		.map((item, index) => ({ ...item, rank: index + 1 }));
}

export function computeFoodSafetyRisk(options = {}) {
	const violations = Math.max(Number(options.violations || 0), 0);
	const support = Math.max(Number(options.support || 0), 0);
	const water = Math.max(Number(options.water || 0), 0);
	const infectious = Math.max(Number(options.infectious || 0), 0);
	const supportBoost = Math.min(22, Math.log1p(support) * 5);
	const violationPenalty = Math.min(58, Math.log1p(violations) * 5.5);
	const waterPenalty = Math.min(12, water * 0.08);
	const infectiousPenalty = Math.min(10, infectious * 0.0003);
	const raw = 68 + supportBoost - violationPenalty - waterPenalty - infectiousPenalty;
	const score = Math.max(0, Math.min(100, Math.round(raw)));
	const level = score >= 75 ? "低風險" : score >= 45 ? "中風險" : "高風險";
	return { score, level, support, violations, water, infectious };
}

export function buildSummaryContext(title, sections = {}) {
	return {
		title,
		generatedAt: new Date().toISOString(),
		sections,
		tables: Object.entries(sections).map(([name, rows]) => ({
			name,
			rows: Array.isArray(rows) ? rows.slice(0, 8) : rows,
		})),
	};
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

export function parseMetricDate(row) {
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

export const DISTRICT_COORDS = {
	中正區: { lat: 25.0324, lng: 121.5198 },
	大同區: { lat: 25.0632, lng: 121.5130 },
	中山區: { lat: 25.0644, lng: 121.5335 },
	松山區: { lat: 25.0497, lng: 121.5773 },
	大安區: { lat: 25.0262, lng: 121.5435 },
	萬華區: { lat: 25.0353, lng: 121.4998 },
	信義區: { lat: 25.0330, lng: 121.5669 },
	士林區: { lat: 25.0950, lng: 121.5246 },
	北投區: { lat: 25.1324, lng: 121.5014 },
	內湖區: { lat: 25.0837, lng: 121.5929 },
	南港區: { lat: 25.0553, lng: 121.6070 },
	文山區: { lat: 24.9886, lng: 121.5736 },
	板橋區: { lat: 25.0114, lng: 121.4618 },
	三重區: { lat: 25.0615, lng: 121.4881 },
	中和區: { lat: 24.9994, lng: 121.4983 },
	永和區: { lat: 25.0097, lng: 121.5148 },
	新莊區: { lat: 25.0359, lng: 121.4504 },
	新店區: { lat: 24.9676, lng: 121.5414 },
	土城區: { lat: 24.9722, lng: 121.4433 },
	蘆洲區: { lat: 25.0855, lng: 121.4706 },
	汐止區: { lat: 25.0642, lng: 121.6587 },
	樹林區: { lat: 24.9907, lng: 121.4205 },
	淡水區: { lat: 25.1697, lng: 121.4409 },
	林口區: { lat: 25.0775, lng: 121.3917 },
	五股區: { lat: 25.0920, lng: 121.4381 },
	泰山區: { lat: 25.0589, lng: 121.4326 },
	深坑區: { lat: 25.0023, lng: 121.6157 },
	三峽區: { lat: 24.9343, lng: 121.3689 },
	鶯歌區: { lat: 24.9564, lng: 121.3500 },
	八里區: { lat: 25.1467, lng: 121.4033 },
	瑞芳區: { lat: 25.1089, lng: 121.8050 },
	萬里區: { lat: 25.1780, lng: 121.6890 },
	金山區: { lat: 25.2236, lng: 121.6369 },
	石碇區: { lat: 24.9919, lng: 121.6587 },
};

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
