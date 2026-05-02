from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    from html.parser import HTMLParser
    import json

    import pandas as pd
    import requests
    from sqlalchemy import create_engine
    from utils.fda_food_vendor import extract_district
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    from_crs = 4326
    geometry_type = "Point"
    source_url = "https://imap.health.gov.taipei/Index.aspx"
    search_url = "https://imap.health.gov.taipei/App_Prog/MapMetro2.aspx"
    aggregate_reference_url = "https://data.gov.tw/dataset/131026"

    class TaipeiHealthMapFormParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.inputs = []
            self.selects = []
            self._active_select = None
            self.payload_text = []
            self._capture_payload = False

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "input" and attrs.get("name"):
                self.inputs.append(attrs)
            elif tag == "select" and attrs.get("name"):
                self._active_select = {
                    "name": attrs.get("name"),
                    "value": "",
                    "has_value": False,
                    "has_selected": False,
                }
            elif tag == "option" and self._active_select is not None:
                if (
                    not self._active_select["has_value"]
                    and not self._active_select["has_selected"]
                ) or "selected" in attrs:
                    self._active_select["value"] = attrs.get("value", "")
                    self._active_select["has_value"] = True
                    self._active_select["has_selected"] = "selected" in attrs
            elif tag == "span" and attrs.get("id") == "ContentPlaceHolder1_cblChartValue1":
                self._capture_payload = True

        def handle_endtag(self, tag):
            if tag == "select" and self._active_select is not None:
                self.selects.append(self._active_select)
                self._active_select = None
            elif tag == "span" and self._capture_payload:
                self._capture_payload = False

        def handle_data(self, data):
            if self._capture_payload:
                self.payload_text.append(data)

    def _parse_form(html):
        parser = TaipeiHealthMapFormParser()
        parser.feed(html)
        form_data = {}
        for item in parser.inputs:
            name = item.get("name")
            input_type = (item.get("type") or "").lower()
            if input_type in ("checkbox", "radio"):
                if "checked" in item:
                    form_data[name] = item.get("value", "on")
            else:
                form_data[name] = item.get("value", "")
        for item in parser.selects:
            form_data[item["name"]] = item["value"]
        return form_data

    def _parse_payload(html):
        parser = TaipeiHealthMapFormParser()
        parser.feed(html)
        return "".join(parser.payload_text).strip()

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "TaipeiCityDashboardPrivate/health-audit-violation",
        }
    )
    response = session.get(search_url, timeout=60)
    response.raise_for_status()
    form_data = _parse_form(response.text)

    form_data.update(
        {
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnSearch",
            "__EVENTARGUMENT": "",
            "ctl00$ContentPlaceHolder1$type1": "radioFood",
            "ctl00$ContentPlaceHolder1$Food_Stations": "radioArea",
            "ctl00$ContentPlaceHolder1$cblstore_check_result$3": "B1",
            "ctl00$ContentPlaceHolder1$cblstore_check_result$4": "B2",
        }
    )

    response = session.post(
        search_url,
        data=form_data,
        headers={"Referer": search_url},
        timeout=120,
    )
    response.raise_for_status()
    payload = _parse_payload(response.text)
    if not payload:
        raise ValueError("No Taipei health audit violation records found.")

    raw_data = pd.DataFrame(json.loads(payload))
    raw_data = raw_data.dropna(how="all")
    raw_data = raw_data[
        raw_data["check_result"].fillna("").astype(str).str.contains("B1|B2", na=False)
    ].copy()

    result_labels = {
        "B1": "限期改善",
        "B2": "複查不合格",
    }

    data = raw_data.rename(
        columns={
            "id": "source_row_no",
            "store_regNum": "registration_no",
            "store_name": "name",
            "store_address": "address",
            "store_tel": "phone",
            "check_result": "inspection_result_code",
            "check_date": "audit_date",
            "store_memo": "violation_reason",
            "latitude": "lat",
            "longitude": "lng",
        }
    )
    for col in [
        "source_row_no",
        "registration_no",
        "name",
        "address",
        "phone",
        "inspection_result_code",
        "audit_date",
        "violation_reason",
    ]:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["city"] = "臺北市"
    data["district"] = data["address"].apply(extract_district)
    data["business_category"] = "食品業者"
    data["inspection_result"] = data["inspection_result_code"].map(result_labels).fillna(
        data["inspection_result_code"]
    )
    data["violation_reason"] = data["violation_reason"].where(
        data["violation_reason"] != "",
        data["inspection_result"],
    )
    data["source_type"] = "衛生稽查違規"
    data["source_dataset"] = "臺北市政府衛生局食藥粧網路地圖"
    data["source_url"] = source_url
    data["aggregate_reference_url"] = aggregate_reference_url
    data["location_method"] = "來源網站座標"
    data["lng"] = pd.to_numeric(data["lng"], errors="coerce")
    data["lat"] = pd.to_numeric(data["lat"], errors="coerce")
    data["data_time"] = pd.to_datetime(data["audit_date"], errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )
    lasttime_in_data = data["data_time"].dropna().max()

    data = data[data["lng"].notna() & data["lat"].notna()].copy()
    if data.empty:
        raise ValueError("No geocoded Taipei health audit violation records found.")

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=from_crs,
    )
    ready_data = gdata[
        [
            "data_time",
            "source_row_no",
            "registration_no",
            "name",
            "city",
            "district",
            "address",
            "phone",
            "audit_date",
            "business_category",
            "inspection_result",
            "violation_reason",
            "source_type",
            "source_dataset",
            "source_url",
            "aggregate_reference_url",
            "location_method",
            "lng",
            "lat",
            "wkb_geometry",
        ]
    ]

    engine = create_engine(ready_data_db_uri)
    save_geodataframe_to_postgresql(
        engine,
        gdata=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
        geometry_type=geometry_type,
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_city_dashboard",
    dag_folder="health_audit_violation_tpe",
)
dag.create_dag(etl_func=_transfer)
