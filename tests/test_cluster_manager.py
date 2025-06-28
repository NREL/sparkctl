import time
from pathlib import Path

import psutil
from pyspark.sql import SparkSession

from sparkctl import (
    ClusterManager,
    SparkConfig,
)


def test_cluster_manager(setup_local_env: tuple[SparkConfig, Path]):
    config, output_dir = setup_local_env
    config.runtime.start_connect_server = True
    config.directories.base = output_dir
    config.directories.spark_scratch = output_dir / "spark_scratch"
    config.directories.metastore_dir = output_dir / "metastore_db"
    config.resource_monitor.enabled = True
    assert not is_rmon_running()
    mgr = ClusterManager(config)
    mgr.configure()
    try:
        mgr.start()
        spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
        df = spark.createDataFrame([(1, 2), (3, 4)], ["a", "b"])
        assert df.count() == 2
        assert is_rmon_running()
    finally:
        mgr.stop()
        assert wait_for_rmon_to_stop()


def wait_for_rmon_to_stop(timeout: int = 30):
    end = time.time() + timeout
    while time.time() < end:
        if not is_rmon_running():
            return True
        time.sleep(0.2)
    return False


def is_rmon_running() -> bool:
    for proc in psutil.process_iter(["name", "cmdline"]):
        if "python" in proc.info["name"] and any(("rmon" in x for x in proc.info["cmdline"])):
            return True
    return False
