#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_OUTPUT_DIR = "Taipei-City-Dashboard-FE/public/mapData"

MARKET_TABLES = {
    "food_safety_market_tpe": [
        "data_time",
        "market_id",
        "city",
        "district",
        "name",
        "type",
        "address",
        "stall_total",
        "vegetable_stalls",
        "fruit_stalls",
        "meat_stalls",
        "seafood_stalls",
        "poultry_stalls",
        "grain_stalls",
        "flower_stalls",
        "grocery_stalls",
        "general_merchandise_stalls",
        "food_stalls",
        "other_stalls",
        "lng",
        "lat",
    ],
    "food_safety_market_ntpe": [
        "data_time",
        "market_id",
        "name",
        "city",
        "city_code",
        "district",
        "district_code",
        "address",
        "phone",
        "type",
        "stall_total",
        "produce_stalls",
        "meat_stalls",
        "seafood_stalls",
        "poultry_stalls",
        "grain_stalls",
        "grocery_stalls",
        "flower_stalls",
        "food_stalls",
        "general_merchandise_stalls",
        "other_stalls",
        "vacant_stalls",
        "lng",
        "lat",
    ],
}


def _quote_ident(name):
    return '"' + name.replace('"', '""') + '"'


def build_geojson_sql(table_name, columns):
    select_cols = ",\n            ".join(
        f"{_quote_ident(column)}::text AS {_quote_ident(column)}"
        if column == "data_time"
        else _quote_ident(column)
        for column in columns
    )
    return f"""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', row_data.geometry,
                    'properties', to_jsonb(row_data) - 'geometry'
                )
            ), '[]'::jsonb)
        )
        FROM (
            SELECT
                {select_cols},
                ST_AsGeoJSON(wkb_geometry)::jsonb AS geometry
            FROM public.{_quote_ident(table_name)}
            ORDER BY NULLIF(regexp_replace(market_id, '\\D', '', 'g'), '')::int NULLS LAST,
                     market_id
        ) row_data
    """


def load_geojson(table_name, columns, container, user, database):
    command = [
        "docker",
        "exec",
        container,
        "psql",
        "-U",
        user,
        "-d",
        database,
        "--tuples-only",
        "--no-align",
        "-c",
        build_geojson_sql(table_name, columns),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout.strip())


def write_geojson(geojson, output_path):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(geojson, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Export food safety market PostGIS tables to frontend GeoJSON."
    )
    parser.add_argument("--container", default="postgres-data")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--database", default="dashboard")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    for table_name, columns in MARKET_TABLES.items():
        geojson = load_geojson(
            table_name,
            columns,
            args.container,
            args.user,
            args.database,
        )
        output = write_geojson(
            geojson,
            Path(args.output_dir) / f"{table_name}.geojson",
        )
        print(f"Wrote {len(geojson.get('features', []))} features to {output}")


if __name__ == "__main__":
    main()
