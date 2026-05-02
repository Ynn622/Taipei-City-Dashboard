from operators.common_pipeline import CommonDag
from airflow.models import Variable
import random
import json
import urllib.parse
import time
import requests

# Configuration
OPEN_DATA_URL = "https://data.taipei/api/v1/dataset/29869b6f-1cd3-4ce8-8c78-eb85aeea8583"
TOWIN_API_URL = "http://localhost:3011/search"
SAMPLE_SIZE_PER_COMPANY = 30
LLM_BATCH_SIZE = 35

# Allergen categories reference
ALLERGEN_CATEGORIES = {
    "海鮮類": ["蝦", "蟹", "龍蝦", "貝", "螺", "章魚", "鮭魚", "鯖魚", "魚"],
    "乳製品": ["牛奶", "起司", "乳", "奶"],
    "花生": ["花生"],
    "麩質穀物": ["小麥", "麵粉", "麩質"],
    "蠶豆": ["蠶豆"],
    "酒精": ["酒精", "酒"],
}


def _food_allergen_classification(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.extract_stage import download_file
    from utils.load_stage import (
        save_dataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )

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
                return result.get("lat"), result.get("lon")
        except Exception as e:
            print(f"Geocode error for {brand_name}: {e}")
        return None, None

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
                "max_new_tokens": 2000,
            },
        }

        try:
            resp = requests.post(url, headers=headers, json=body, timeout=60)
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

            return [{"has_allergens": False, "allergens": []} for _ in products_batch]
        except Exception as e:
            print(f"LLM classification error: {e}")
            return [{"has_allergens": False, "allergens": []} for _ in products_batch]

    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # 1. Extract
    print("Step 1: Fetching all records from API...")
    records = fetch_all_records()
    print(f"  Total records fetched: {len(records)}")

    # 2. Transform - aggregate
    print("Step 2: Aggregating by company and product...")
    products = aggregate_by_company_product(records)
    print(f"  Unique products: {len(products)}")

    # Group by company
    company_groups = {}
    for p in products:
        company = p["company_name"]
        if company not in company_groups:
            company_groups[company] = []
        company_groups[company].append(p)

    print(f"  Total companies: {len(company_groups)}")

    # Sample
    sampled_products = []
    for company, prods in company_groups.items():
        sampled = sample_products(prods, SAMPLE_SIZE_PER_COMPANY)
        sampled_products.extend(sampled)

    print(f"  Sampled products: {len(sampled_products)}")

    # 3. Geocode
    print("Step 3: Geocoding brand names...")
    brand_coords = {}
    for company, prods in company_groups.items():
        brand = prods[0]["brand_name"] if prods else company
        if brand not in brand_coords:
            lat, lon = geocode_brand(brand)
            brand_coords[brand] = (lat, lon)
            time.sleep(0.1)

    print(f"  Brands geocoded: {len(brand_coords)}")

    # 4. Classify with LLM
    print("Step 4: Classifying allergens with LLM...")
    api_url = Variable.get("TWCC_API_URL", default_var="https://api-ams.twcc.ai/api")
    api_key = Variable.get("TWCC_API_KEY", default_var="")
    model = Variable.get("TWCC_MODEL", default_var="llama3.3-ffm-70b-16k-chat")

    llm_results = []
    batches = list(chunk_list(sampled_products, LLM_BATCH_SIZE))
    print(f"  Total batches: {len(batches)}")

    for i, batch in enumerate(batches):
        print(f"  Processing batch {i+1}/{len(batches)}...")
        results = classify_allergens_llm(batch, api_url, api_key, model)
        llm_results.extend(results)
        time.sleep(2)

    # 5. Merge results
    print("Step 5: Preparing final data...")
    final_records = []
    for product, result in zip(sampled_products, llm_results):
        brand = product["brand_name"]
        lat, lon = brand_coords.get(brand, (None, None))

        allergens = result.get("allergens", [])
        has_allergens = result.get("has_allergens", False)

        final_records.append(
            {
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
    print(f"  Final records: {len(ready_data)}")
    print(f"  With coordinates: {ready_data['lat'].notna().sum()}")
    print(f"  With allergens: {ready_data['has_allergens'].sum()}")

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    engine = create_engine(ready_data_db_uri)
    save_dataframe_to_postgresql(
        engine,
        data=ready_data,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
    )
    update_lasttime_in_data_to_dataset_info(
        engine,
        dag_id,
        ready_data["data_time"].max(),
    )

    print("Done!")


dag = CommonDag(
    proj_folder="proj_city_dashboard", dag_folder="food_allergen_classification"
)
dag.create_dag(etl_func=_food_allergen_classification)
