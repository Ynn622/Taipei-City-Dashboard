#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

try:
    from sqlalchemy import create_engine, text
except ModuleNotFoundError:
    create_engine = None
    text = None


DEFAULT_DB_URI = (
    os.getenv("FDA_GOOD_RESTAURANTS_DB_URI")
    or os.getenv("DATABASE_URL")
    or "postgresql://postgres:123456@postgres-data:5432/dashboard"
)
DEFAULT_OUTPUT = (
    "Taipei-City-Dashboard-FE/public/mapData/fda_good_restaurants.geojson"
)


FEATURES_SQL = """
        SELECT
            data_time::text AS data_time,
            city,
            district,
            award_year,
            restaurant_name,
            address,
            lng,
            lat,
            rating_result,
            ST_AsGeoJSON(wkb_geometry)::json AS geometry
        FROM public.fda_good_restaurants
        WHERE award_year = (
            SELECT MAX(award_year)
            FROM public.fda_good_restaurants
        )
        ORDER BY city, district, restaurant_name, address
"""

GEOJSON_SQL = """
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
            data_time::text AS data_time,
            city,
            district,
            award_year,
            restaurant_name,
            address,
            lng,
            lat,
            rating_result,
            ST_AsGeoJSON(wkb_geometry)::jsonb AS geometry
        FROM public.fda_good_restaurants
        WHERE award_year = (
            SELECT MAX(award_year)
            FROM public.fda_good_restaurants
        )
        ORDER BY city, district, restaurant_name, address
    ) row_data
"""


def load_features_with_sqlalchemy(db_uri):
    if create_engine is None:
        raise ModuleNotFoundError("sqlalchemy")

    sql = text(FEATURES_SQL)
    engine = create_engine(db_uri)
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    features = []
    for row in rows:
        record = dict(row)
        geometry = record.pop("geometry")
        if isinstance(geometry, str):
            geometry = json.loads(geometry)
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": record,
            }
        )
    return features


def load_geojson_with_docker_psql(db_uri, container_name=None):
    parsed = urlparse(db_uri)
    container = container_name or parsed.hostname or "postgres-data"
    db_name = parsed.path.lstrip("/") or "dashboard"
    user = parsed.username or "postgres"
    command = [
        "docker",
        "exec",
        container,
        "psql",
        "-U",
        user,
        "-d",
        db_name,
        "--tuples-only",
        "--no-align",
        "-c",
        GEOJSON_SQL,
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "docker psql export failed:\n"
            f"command: {' '.join(command[:8])} ...\n"
            f"stderr: {result.stderr.strip()}"
        )
    return json.loads(result.stdout.strip())


def load_geojson(db_uri, docker_container=None):
    try:
        features = load_features_with_sqlalchemy(db_uri)
        return {"type": "FeatureCollection", "features": features}
    except ModuleNotFoundError as error:
        if error.name not in {"psycopg2", "sqlalchemy"}:
            raise
        print(f"Python PostgreSQL driver not found ({error.name}); fallback to docker psql.")
        try:
            return load_geojson_with_docker_psql(db_uri, docker_container)
        except Exception as docker_error:
            raise RuntimeError(str(docker_error)) from None


def write_geojson(geojson, output_path):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            geojson,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Export fda_good_restaurants from PostGIS to frontend GeoJSON."
    )
    parser.add_argument("--db-uri", default=DEFAULT_DB_URI)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--docker-container",
        default=None,
        help="Fallback docker container name for psql, default uses the DB URI host.",
    )
    args = parser.parse_args()

    geojson = load_geojson(args.db_uri, args.docker_container)
    output = write_geojson(geojson, args.output)
    print(f"Wrote {len(geojson.get('features', []))} features to {output}")


if __name__ == "__main__":
    main()
