export const districts = [
	"北投區",
	"士林區",
	"內湖區",
	"南港區",
	"松山區",
	"信義區",
	"中山區",
	"大同區",
	"中正區",
	"萬華區",
	"大安區",
	"文山區",
	"新莊區",
	"淡水區",
	"汐止區",
	"板橋區",
	"三重區",
	"樹林區",
	"土城區",
	"蘆洲區",
	"中和區",
	"永和區",
	"新店區",
	"鶯歌區",
	"三峽區",
	"瑞芳區",
	"五股區",
	"泰山區",
	"林口區",
	"深坑區",
	"石碇區",
	"坪林區",
	"三芝區",
	"石門區",
	"八里區",
	"平溪區",
	"雙溪區",
	"貢寮區",
	"金山區",
	"萬里區",
	"烏來區",
];

export const taipeiDistricts = districts.slice(0, 12);
export const newTaipeiDistricts = districts.slice(12);
export const cityCategories = ["臺北市", "新北市"];

export function isCityLevelDistrictChart(chartConfig) {
	const categories = chartConfig?.categories || [];
	return (
		categories.length > 0 &&
		categories.every((category) => cityCategories.includes(category))
	);
}

export function parseDistrictChartData(chartConfig, series = []) {
	const output = districts.reduce(
		(accumulator, district) => ({
			...accumulator,
			[district]: 0,
		}),
		{ highest: 0, sum: 0 },
	);
	let highest = 0;
	let sum = 0;
	const categories = chartConfig?.categories || [];

	if (isCityLevelDistrictChart(chartConfig)) {
		const cityTotals = {
			臺北市: 0,
			新北市: 0,
		};
		series.forEach((serie) => {
			categories.forEach((category, index) => {
				if (cityCategories.includes(category)) {
					cityTotals[category] += Number(serie.data?.[index] || 0);
				}
			});
		});
		taipeiDistricts.forEach((district) => {
			output[district] = cityTotals["臺北市"];
		});
		newTaipeiDistricts.forEach((district) => {
			output[district] = cityTotals["新北市"];
		});
		output["臺北市"] = cityTotals["臺北市"];
		output["新北市"] = cityTotals["新北市"];
		highest = Math.max(...Object.values(cityTotals));
		sum = Object.values(cityTotals).reduce(
			(partialSum, value) => partialSum + value,
			0,
		);
	} else if (series.length === 1) {
		series[0].data?.forEach((item) => {
			const value = Number(item.y || 0);
			output[item.x] = value;
			if (value > highest) {
				highest = value;
			}
			sum += value;
		});
	} else {
		series.forEach((serie) => {
			for (let i = 0; i < categories.length; i++) {
				if (!output[categories[i]]) {
					output[categories[i]] = 0;
				}
				output[categories[i]] += Number(serie.data?.[i] || 0);
			}
		});
		highest = Object.values(output).sort((a, b) => b - a)[0] || 0;
		sum = Object.values(output).reduce(
			(partialSum, value) => partialSum + value,
			0,
		);
	}

	output.highest = highest;
	output.sum = sum;

	return output;
}
