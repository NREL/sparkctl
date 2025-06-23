from pathlib import Path

import rich_click as click
import toml

from sparkctl.config import (
    DEFAULT_SETTINGS_FILENAME,
    RUNTIME,
    sparkctl_settings,
)
from sparkctl.cluster_manager import ClusterManager
from sparkctl.loggers import setup_logging
from sparkctl.models import (
    BinaryLocations,
    ComputeEnvironment,
    ComputeParams,
    SparkConfig,
    SparkRuntimeParams,
    RuntimeDirectories,
)


@click.group("sparkctl")
def cli():
    """sparkctl comands"""


_default_config_epilog = """
Examples:\n
$ sparkctl default-config ~/apache-spark/spark-4.0.0-bin-hadoop3\n
"""


@click.command(name="default-config", epilog=_default_config_epilog)
@click.argument("spark_path", type=click.Path(exists=True), callback=lambda *x: Path(x[2]))
@click.option(
    "-d",
    "--directory",
    default=Path.home(),
    show_default=True,
    help="Directory in which to create the sparkctl config file.",
    callback=lambda *x: Path(x[2]),
)
@click.option(
    "-H",
    "--hadoop-path",
    help="Directory containing Hadoop binaries.",
    callback=lambda *x: None if x[2] is None else Path(x[2]),
)
@click.option(
    "-h",
    "--hive-tarball",
    help="File containing Hive binaries.",
    callback=lambda *x: None if x[2] is None else Path(x[2]),
)
@click.option(
    "-p",
    "--postgresql-jar-file",
    help="Path to PostgreSQL jar file.",
    callback=lambda *x: None if x[2] is None else Path(x[2]),
)
def create_default_config(
    spark_path: Path,
    directory: Path,
    hadoop_path: Path | None,
    hive_tarball: Path | None,
    postgresql_jar_file: Path | None,
):
    """Create a sparkctl config file.
    This is a one-time requirement when installing sparkctl in a new environment."""
    config = _create_default_config(spark_path, directory)
    if hadoop_path is not None:
        config.binaries.hadoop_path = hadoop_path
    if hive_tarball is not None:
        config.binaries.hive_tarball = hive_tarball
    if postgresql_jar_file is not None:
        config.binaries.postgresql_jar_file = postgresql_jar_file
    data = config.model_dump(mode="json", exclude={"directories"})
    filename = directory / DEFAULT_SETTINGS_FILENAME
    with open(filename, "w", encoding="utf-8") as f_out:
        toml.dump(data, f_out)
    print(f"Wrote sparkctl settings to {filename}")


def _create_default_config(spark_path: Path, directory: Path) -> SparkConfig:
    """Create the default Spark configuration."""
    return SparkConfig(
        compute=ComputeParams(environment=ComputeEnvironment.SLURM),
        binaries=BinaryLocations(spark_path=spark_path),
        directories=RuntimeDirectories(base=directory),
        runtime=SparkRuntimeParams(**RUNTIME),
    )


CONFIGURE_OPTIONS = (
    click.option(
        "-d",
        "--directory",
        default=Path(),
        show_default=True,
        help="Base directory for the cluster configuration",
        type=click.Path(),
        callback=lambda *x: Path(x[2]),
    ),
    click.option(
        "-s",
        "--spark-scratch",
        default=Path("spark_scratch"),
        show_default=True,
        help=RuntimeDirectories.model_fields["spark_scratch"].description,
        callback=lambda *x: Path(x[2]),
    ),
    click.option(
        "-e",
        "--executor-cores",
        default=sparkctl_settings.runtime.get("executor_cores"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["executor_cores"].description,
    ),
    click.option(
        "-M",
        "--driver-memory-gb",
        default=sparkctl_settings.runtime.get("driver_memory_gb"),
        show_default=True,
        type=int,
        help=SparkRuntimeParams.model_fields["driver_memory_gb"].description,
    ),
    click.option(
        "-o",
        "--node-memory-overhead-gb",
        default=sparkctl_settings.runtime.get("node_memory_overhead_gb"),
        show_default=True,
        type=int,
        help=SparkRuntimeParams.model_fields["node_memory_overhead_gb"].description,
    ),
    click.option(
        "-D",
        "--dynamic-allocation",
        is_flag=True,
        default=sparkctl_settings.runtime.get("enable_dynamic_allocation"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["enable_dynamic_allocation"].description,
    ),
    click.option(
        "-m",
        "--shuffle-partition-multiplier",
        default=sparkctl_settings.runtime.get("shuffle_partition_multiplier"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["shuffle_partition_multiplier"].description,
    ),
    click.option(
        "-L",
        "--local-storage",
        is_flag=True,
        default=sparkctl_settings.runtime.get("use_local_storage"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["use_local_storage"].description,
    ),
    click.option(
        "-c",
        "--connect-server",
        is_flag=True,
        default=sparkctl_settings.runtime.get("start_connect_server"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["start_connect_server"].description,
    ),
    click.option(
        "-H",
        "--history-server",
        is_flag=True,
        default=sparkctl_settings.runtime.get("start_history_server"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["start_history_server"].description,
    ),
    click.option(
        "-t",
        "--thrift-server",
        is_flag=True,
        default=sparkctl_settings.runtime.get("start_thrift_server"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["start_thrift_server"].description,
    ),
    click.option(
        "-h",
        "--hive-metastore",
        is_flag=True,
        default=sparkctl_settings.runtime.get("enable_hive_metastore"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["enable_hive_metastore"].description,
    ),
    click.option(
        "-p",
        "--postgres-hive-metastore",
        is_flag=True,
        default=sparkctl_settings.runtime.get("enable_postgres_hive_metastore"),
        show_default=True,
        help=SparkRuntimeParams.model_fields["enable_postgres_hive_metastore"].description,
    ),
    click.option(
        "-w",
        "--metastore-dir",
        default=Path(),
        show_default=True,
        help=RuntimeDirectories.model_fields["metastore_dir"].description,
        callback=lambda *x: Path(x[2]),
    ),
)


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


_configure_epilog = """
Examples:\n
$ sparkctl configure --shuffle-partition-multiplier 4\n
$ sparkctl configure --local-storage\n
$ sparkctl configure --local-storage --thrift-server\n
"""


@click.command(epilog=_configure_epilog)
@add_options(CONFIGURE_OPTIONS)
def configure(
    directory: Path,
    spark_scratch: Path,
    executor_cores: int,
    driver_memory_gb: int,
    node_memory_overhead_gb: int,
    dynamic_allocation: bool,
    shuffle_partition_multiplier: int,
    local_storage: bool,
    connect_server: bool,
    history_server: bool,
    thrift_server: bool,
    hive_metastore: bool,
    postgres_hive_metastore: bool,
    metastore_dir: Path,
):
    """Create a Spark cluster configuration. Use this command to create a Spark configuration
    that can be manually modified before starting.
    """
    _configure_common(
        directory=directory,
        spark_scratch=spark_scratch,
        executor_cores=executor_cores,
        driver_memory_gb=driver_memory_gb,
        node_memory_overhead_gb=node_memory_overhead_gb,
        dynamic_allocation=dynamic_allocation,
        shuffle_partition_multiplier=shuffle_partition_multiplier,
        local_storage=local_storage,
        connect_server=connect_server,
        history_server=history_server,
        thrift_server=thrift_server,
        hive_metastore=hive_metastore,
        postgres_hive_metastore=postgres_hive_metastore,
        metastore_dir=metastore_dir,
    )


_configure_and_start_epilog = """
Examples:\n
$ sparkctl configure-and-start --shuffle-partition-multiplier 4\n
$ sparkctl configure-and-start --local-storage\n
$ sparkctl configure-and-start --local-storage --thrift-server\n
"""


@click.command(epilog=_configure_and_start_epilog)
@add_options(CONFIGURE_OPTIONS)
def configure_and_start(
    directory: Path,
    spark_scratch: Path,
    executor_cores: int,
    driver_memory_gb: int,
    node_memory_overhead_gb: int,
    dynamic_allocation: bool,
    shuffle_partition_multiplier: int,
    local_storage: bool,
    connect_server: bool,
    history_server: bool,
    thrift_server: bool,
    hive_metastore: bool,
    postgres_hive_metastore: bool,
    metastore_dir: Path,
):
    """Create a Spark cluster configuration and start the cluster."""
    mgr = _configure_common(
        directory=directory,
        spark_scratch=spark_scratch,
        executor_cores=executor_cores,
        driver_memory_gb=driver_memory_gb,
        node_memory_overhead_gb=node_memory_overhead_gb,
        dynamic_allocation=dynamic_allocation,
        shuffle_partition_multiplier=shuffle_partition_multiplier,
        local_storage=local_storage,
        connect_server=connect_server,
        history_server=history_server,
        thrift_server=thrift_server,
        hive_metastore=hive_metastore,
        postgres_hive_metastore=postgres_hive_metastore,
        metastore_dir=metastore_dir,
    )
    mgr.start()


def _configure_common(
    directory: Path,
    spark_scratch: Path,
    executor_cores: int,
    driver_memory_gb: int,
    node_memory_overhead_gb: int,
    dynamic_allocation: bool,
    shuffle_partition_multiplier: int,
    local_storage: bool,
    connect_server: bool,
    history_server: bool,
    thrift_server: bool,
    hive_metastore: bool,
    postgres_hive_metastore: bool,
    metastore_dir: Path,
) -> ClusterManager:
    setup_logging(filename="sparkctl.log", mode="a")
    config = SparkConfig(
        binaries=BinaryLocations(
            spark_path=sparkctl_settings.binaries.spark_path,
            hadoop_path=sparkctl_settings.binaries.get("hadoop_path"),
            hive_tarball=sparkctl_settings.binaries.get("hive_tarball"),
            postgresql_jar_file=sparkctl_settings.binaries.get("postgresql_jar_file"),
        ),
        runtime=SparkRuntimeParams(
            executor_cores=executor_cores,
            driver_memory_gb=driver_memory_gb,
            node_memory_overhead_gb=node_memory_overhead_gb,
            enable_dynamic_allocation=dynamic_allocation,
            shuffle_partition_multiplier=shuffle_partition_multiplier,
            use_local_storage=local_storage,
            start_connect_server=connect_server,
            start_history_server=history_server,
            start_thrift_server=thrift_server,
            enable_hive_metastore=hive_metastore,
            enable_postgres_hive_metastore=postgres_hive_metastore,
        ),
        directories=RuntimeDirectories(
            base=directory,
            spark_scratch=spark_scratch,
            metastore_dir=metastore_dir,
        ),
        compute=sparkctl_settings.get("compute", {"environment": "slurm"}),
    )
    mgr = ClusterManager(config)
    mgr.configure()
    return mgr


_start_epilog = """
Examples:\n
$ sparkctl start\n
$ sparkctl start --directory ./my-spark-config\n
"""


@click.command(epilog=_start_epilog)
@click.option(
    "-d",
    "--directory",
    default=Path(),
    show_default=True,
    help="Base directory for the cluster configuration",
    type=click.Path(),
    callback=lambda *x: Path(x[2]),
)
def start(directory: Path) -> None:
    """Start a Spark cluster with an existing configuration. This is useful if you have manually
    modified a Spark configuration created with `sparkctl configure`."""
    setup_logging(filename="sparkctl.log", mode="a")
    mgr = ClusterManager.load(directory)
    mgr.start()


_stop_epilog = """
Examples:\n
$ sparkctl stop\n
$ sparkctl stop --directory ./my-spark-config\n
"""


@click.command(epilog=_stop_epilog)
@click.option(
    "-d",
    "--directory",
    default=Path(),
    show_default=True,
    help="Base directory for the cluster configuration",
    type=click.Path(),
    callback=lambda *x: Path(x[2]),
)
def stop(directory: Path) -> None:
    """Stop a Spark cluster."""
    mgr = ClusterManager.load(directory)
    mgr.stop()


@click.command()
@click.argument("directory", callback=lambda *x: Path(x[2]))
def clean(directory: Path) -> None:
    """Delete all Spark runtime files in the directory."""
    mgr = ClusterManager.load(directory)
    mgr.clean()


cli.add_command(create_default_config)
cli.add_command(configure)
cli.add_command(configure_and_start)
cli.add_command(start)
cli.add_command(stop)
# cli.add_command(clean)
