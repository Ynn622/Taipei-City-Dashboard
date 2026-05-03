from operators.common_pipeline import CommonDag
from airflow.models import Variable
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import logging
import random
import json
import urllib.parse
import time
import requests

logger = logging.getLogger(__name__)

# Configuration
OPEN_DATA_URL = "https://data.taipei/api/v1/dataset/29869b6f-1cd3-4ce8-8c78-eb85aeea8583"
TOWIN_API_URL = Variable.get("TOWIN_API_URL", default_var="http://localhost:3011/search")
SAMPLE_SIZE_PER_COMPANY = 30
LLM_BATCH_SIZE = 35
MAX_CONCURRENT = 10


def _food_allergen_classification(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import download_file
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    def fetch_all_records():
        all_records = []
        offset = 0
        limit = 1000
        while True:
            url = f"{OPEN_DATA_URL}?scope=resourceAquire&limit={limit}&offset={offset}"
            resp = requests.get(url, timeout=60)
            data = resp.json()
            results = data["result"]["results"]
            if not results:
                break
            all_records.extend(results)
            offset += limit
            if len(results) < limit:
                break
        return all_records

    def aggregate_by_company_product(records):
        company_products = {}
        for r in records:
            company = r["公司名稱"]
            brand = r["品牌名稱"]
            product = r["產品名稱"]
            ingredient = r["原料名稱"]

            key = (company, brand, product)
            if key not in company_products:
                company_products[key] = {
                    "company_name": company,
                    "brand_name": brand,
                    "product_name": product,
                    "ingredients": [],
                }
            if ingredient:
                company_products[key]["ingredients"].append(ingredient)

        return list(company_products.values())

    def sample_products(products, n=SAMPLE_SIZE_PER_COMPANY):
        if len(products) <= n:
            return products
        return random.sample(products, n)

    def geocode_brand(brand_name):
        try:
            encoded = urllib.parse.quote(brand_name)
            url = f"{TOWIN_API_URL}?q={encoded}&limit=1"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                county = result.get("county") or result.get("city")
                if county:
                    if "台北" in county or "臺北" in county: county = "臺北市"
                    elif "新北" in county: county = "新北市"
                return result.get("lat"), result.get("lon"), county
        except Exception as e:
            logger.error(f"Geocode error for {brand_name}: {e}")
        return None, None, None

    def classify_allergens_llm(products_batch, api_url, api_key, model):
        system_prompt = """你是一位營養師與食品安全專家。請根據提供的產品名稱與原料清單，判斷是否含有以下特殊過敏原：

海鮮類：蝦、蟹、龍蝦、貝、螺、章魚、鮭魚、鯖魚等
乳製品：牛奶、起司
花生
麩質穀物
蠶豆
酒精

請對每個產品回傳 JSON 格式：
{"results": [{"has_allergens": true/false, "allergens": ["類別1", "類別2"]}]}

注意：回傳必須是純 JSON，不要加上其他說明文字。"""

        batch_json = json.dumps(
            [
                {
                    "product_name": p["product_name"],
                    "ingredients": p["ingredients"],
                }
                for p in products_batch
            ],
            ensure_ascii=False,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": batch_json},
        ]

        url = f"{api_url}/models/conversation"
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key,
        }
        body = {
            "model": model,
            "messages": messages,
            "parameters": {
                "temperature": 0.1,
                "max_new_tokens": 5000,
            },
        }

        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=180)
                resp.raise_for_status()
                data = resp.json()

                content = ""
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                elif "generated_text" in data:
                    content = data["generated_text"]

                try:
                    result = json.loads(content)
                    if "results" in result:
                        return result["results"]
                except Exception:
                    pass
            except Exception as e:
                if attempt < 2:
                    logger.error(f"Retry batch after error: {e}")
                    time.sleep(5)
                    continue
                logger.error(f"Batch failed after 3 attempts: {e}")

        raise RuntimeError(
            f"LLM classification failed after 3 attempts for batch of {len(products_batch)} products."
        )

    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    api_url = Variable.get("TWCC_API_URL", default_var="https://api-ams.twcc.ai/api")
    api_key = Variable.get("TWCC_API_KEY", default_var="")
    model = Variable.get("TWCC_MODEL", default_var="llama3.3-ffm-70b-16k-chat")

    if not api_key:
        raise ValueError("TWCC_API_KEY is not set in Airflow Variables.")

    # 1. Extract
    logger.info("Step 1: Fetching all records from API...")
    records = fetch_all_records()
    logger.info(f"Total records fetched: {len(records)}")

    # 2. Transform - aggregate
    logger.info("Step 2: Aggregating by company and product...")
    products = aggregate_by_company_product(records)
    logger.info(f"Unique products: {len(products)}")

    # Group by company
    company_groups = {}
    for p in products:
        company = p["company_name"]
        if company not in company_groups:
            company_groups[company] = []
        company_groups[company].append(p)

    logger.info(f"Total companies: {len(company_groups)}")

    # Sample
    sampled_products = []
    for company, prods in company_groups.items():
        sampled = sample_products(prods, SAMPLE_SIZE_PER_COMPANY)
        sampled_products.extend(sampled)

    logger.info(f"Sampled products: {len(sampled_products)}")

    # 3. Geocode
    logger.info("Step 3: Geocoding brand names...")
    brand_coords = {}
    for company, prods in company_groups.items():
        brand = prods[0]["brand_name"] if prods else company
        if brand not in brand_coords:
            lat, lon, county = geocode_brand(brand)
            brand_coords[brand] = (lat, lon, county)
            time.sleep(0.1)

    logger.info(f"Brands geocoded: {len(brand_coords)}")

    # 4. Classify with LLM (concurrent, max 10 workers)
    logger.info("Step 4: Classifying allergens with LLM (concurrent)...")

    batches = list(chunk_list(sampled_products, LLM_BATCH_SIZE))
    logger.info(f"Total batches: {len(batches)}, Workers: {MAX_CONCURRENT}")

    llm_results = [None] * len(batches)
    lock = Lock()

    def process_batch(idx_batch):
        idx, batch = idx_batch
        result = classify_allergens_llm(batch, api_url, api_key, model)
        with lock:
            llm_results[idx] = result
        return idx

    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {executor.submit(process_batch, (i, b)): i for i, b in enumerate(batches)}
        completed = 0
        for future in as_completed(futures):
            idx = future.result()
            completed += 1
            if completed % 10 == 0 or completed == len(batches):
                elapsed = time.time() - start
                logger.info(f"Completed {completed}/{len(batches)} batches ({elapsed:.0f}s)")

    llm_time = time.time() - start
    logger.info(f"LLM total time: {llm_time:.1f}s ({llm_time/60:.1f} min)")

    # 5. Merge results
    logger.info("Step 5: Preparing final data...")
    final_records = []
    flat_results = []
    for r in llm_results:
        if r is None:
            raise RuntimeError("LLM classification returned incomplete batch results.")
        flat_results.extend(r)

    for product, result in zip(sampled_products, flat_results):
        brand = product["brand_name"]
        lat, lon, county = brand_coords.get(brand, (None, None, None))

        if county not in ["臺北市", "新北市"]:
            if not lat or not lon:
                continue
            if 25.00 <= lat <= 25.22 and 121.45 <= lon <= 121.67:
                county = "臺北市"
            elif 24.67 <= lat <= 25.30 and 121.28 <= lon <= 122.01:
                county = "新北市"
            else:
                continue

        allergens = result.get("allergens", [])
        has_allergens = result.get("has_allergens", False)

        final_records.append(
            {
                "county": county,
                "company_name": product["company_name"],
                "brand_name": product["brand_name"],
                "product_name": product["product_name"],
                "ingredients": product["ingredients"],
                "has_allergens": has_allergens,
                "allergens": allergens,
                "allergen_count": len(allergens),
                "lat": lat,
                "lon": lon,
                "data_time": pd.Timestamp.now(),
            }
        )

    ready_data = pd.DataFrame(final_records)
    lon_series = pd.Series(ready_data["lon"])
    lat_series = pd.Series(ready_data["lat"])
    ready_data = add_point_wkbgeometry_column_to_df(
        ready_data, x=lon_series, y=lat_series, from_crs=4326
    )
    ready_data = ready_data.drop(columns=["geometry"])
    logger.info(f"Final records: {len(ready_data)}")
    logger.info(f"With coordinates: {ready_data['lat'].notna().sum()}")
    logger.info(f"With allergens: {ready_data['has_allergens'].sum()}")

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    if dag_infos is None:
        raise ValueError("dag_infos is required.")
    if ready_data_db_uri is None:
        raise ValueError("ready_data_db_uri is required.")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    engine = create_engine(ready_data_db_uri)
    save_geodataframe_to_postgresql(
        engine,
        gdata=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
        geometry_type="Point",
    )
    update_lasttime_in_data_to_dataset_info(
        engine,
        dag_id,
        ready_data["data_time"].max(),
    )

    logger.info("Done!")


dag = CommonDag(
    proj_folder="proj_city_dashboard", dag_folder="food_allergen_classification"
)
dag.create_dag(etl_func=_food_allergen_classification)
