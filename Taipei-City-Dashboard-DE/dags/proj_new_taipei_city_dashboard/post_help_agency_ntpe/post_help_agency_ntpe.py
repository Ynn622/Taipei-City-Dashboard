from airflow import DAG
from operators.common_pipeline import CommonDag


def _transfer(**kwargs):
    from sqlalchemy import create_engine
    from utils.load_stage import (
        save_geodataframe_to_postgresql,
        update_lasttime_in_data_to_dataset_info,
    )
    from utils.post_help_agency import build_post_help_agency
    from utils.transform_geometry import add_point_wkbgeometry_column_to_df

    ready_data_db_uri = kwargs.get("ready_data_db_uri")
    dag_infos = kwargs.get("dag_infos")
    dag_id = dag_infos.get("dag_id")
    load_behavior = dag_infos.get("load_behavior")
    default_table = dag_infos.get("ready_data_default_table")
    history_table = dag_infos.get("ready_data_history_table")

    data = build_post_help_agency("新北市")
    lasttime_in_data = data["data_time"].max()
    gdata = add_point_wkbgeometry_column_to_df(
        data,
        data["lng"],
        data["lat"],
        from_crs=4326,
    )

    engine = create_engine(ready_data_db_uri)
    save_geodataframe_to_postgresql(
        engine,
        gdata=gdata,
        load_behavior=load_behavior,
        default_table=default_table,
        history_table=history_table,
        geometry_type="Point",
    )
    update_lasttime_in_data_to_dataset_info(engine, dag_id, lasttime_in_data)


dag = CommonDag(
    proj_folder="proj_new_taipei_city_dashboard",
    dag_folder="post_help_agency_ntpe",
)
dag.create_dag(etl_func=_transfer)
