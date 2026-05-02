from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    import pandas as pd
    from sqlalchemy import create_engine
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df
    from utils.water_quality import fetch_taipei_water_quality

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    data = fetch_taipei_water_quality()
    data["etl_update_time"] = pd.Timestamp.now(tz="Asia/Taipei").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    lasttime_in_data = data["etl_update_time"].max()

    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=4326,
    )
    ready_data = gdata[
        [
            "etl_update_time",
            "source_row_no",
            "name",
            "english_name",
            "city",
            "district",
            "address",
            "water_sources",
            "data_time",
            "qualified",
            "ph",
            "turbidity_ntu",
            "free_residual_chlorine_mg_l",
            "total_hardness_mg_l",
            "total_dissolved_solids_mg_l",
            "coliform_cfu_100ml",
            "source_dataset",
            "source_url",
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
        geometry_type="Point",
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_city_dashboard",
    dag_folder="water_quality_tpe",
)
dag.create_dag(etl_func=_transfer)
