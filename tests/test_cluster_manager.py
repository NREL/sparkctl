from pathlib import Path

from pyspark.sql import SparkSession

from sparkctl import (
    ClusterManager,
    SparkConfig,
)


def test_cluster_manager(setup_local_env: tuple[SparkConfig, Path]):
    config, output_dir = setup_local_env
    config.runtime_params.start_connect_server = True
    config.directories.base = output_dir
    config.directories.spark_scratch = output_dir / "spark_scratch"
    config.directories.metastore_dir = output_dir / "metastore_db"
    mgr = ClusterManager(config)
    mgr.configure()
    try:
        mgr.start()
        spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
        df = spark.createDataFrame([(1, 2), (3, 4)], ["a", "b"])
        assert df.count() == 2
    finally:
        mgr.stop()
