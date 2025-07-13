from sparkctl.models import AppParams, ComputeParams
from pathlib import Path

from dynaconf import Dynaconf, Validator  # type: ignore
from rich import print

from sparkctl.models import BinaryLocations, SparkRuntimeParams, SparkConfig

DEFAULT_SETTINGS_FILENAME = ".sparkctl.toml"
BINARIES = {
    "spark_path": Path("/datasets/images/apache_spark/spark-4.0.0-bin-hadoop3"),
    "java_path": Path("/datasets/images/apache_spark/jdk-21.0.7"),
    "hadoop_path": Path("/datasets/images/apache_spark/hadoop-3.4.1"),
    "hive_tarball": Path("/datasets/images/apache_spark/apache-hive-4.0.1-bin.tar.gz"),
    "postgresql_jar_file": Path("/datasets/images/apache_spark/postgresql-42.7.4.jar"),
}
RUNTIME = {
    "executor_cores": SparkRuntimeParams.model_fields["executor_cores"].default,
    "executor_memory_gb": SparkRuntimeParams.model_fields["executor_memory_gb"].default,
    "driver_memory_gb": SparkRuntimeParams.model_fields["driver_memory_gb"].default,
    "node_memory_overhead_gb": SparkRuntimeParams.model_fields["node_memory_overhead_gb"].default,
    "use_local_storage": SparkRuntimeParams.model_fields["use_local_storage"].default,
    "start_connect_server": SparkRuntimeParams.model_fields["start_connect_server"].default,
    "start_history_server": SparkRuntimeParams.model_fields["start_history_server"].default,
    "start_thrift_server": SparkRuntimeParams.model_fields["start_thrift_server"].default,
    "spark_log_level": SparkRuntimeParams.model_fields["spark_log_level"].default,
    "enable_dynamic_allocation": SparkRuntimeParams.model_fields[
        "enable_dynamic_allocation"
    ].default,
    "shuffle_partition_multiplier": SparkRuntimeParams.model_fields[
        "shuffle_partition_multiplier"
    ].default,
    "enable_hive_metastore": SparkRuntimeParams.model_fields["enable_hive_metastore"].default,
    "enable_postgres_hive_metastore": SparkRuntimeParams.model_fields[
        "enable_postgres_hive_metastore"
    ].default,
    "postgres_password": None,
    "spark_defaults_template_file": None,
}
APP = {
    "console_level": AppParams.model_fields["console_level"].default,
    "file_level": AppParams.model_fields["file_level"].default,
    "reraise_exceptions": AppParams.model_fields["reraise_exceptions"].default,
}

sparkctl_settings = Dynaconf(
    envvar_prefix="SPARKCTL",
    settings_files=[
        DEFAULT_SETTINGS_FILENAME,
    ],
    validators=[
        Validator("BINARIES", default=BinaryLocations(**BINARIES).model_dump(mode="json")),
        Validator("RUNTIME", default=SparkRuntimeParams(**RUNTIME).model_dump(mode="json")),
        Validator("COMPUTE", default=ComputeParams().model_dump(mode="json")),
        Validator("APP", default=AppParams().model_dump(mode="json")),
    ],
)


def make_default_spark_config() -> SparkConfig:
    """Return a SparkConfig created from the user's config file."""
    return SparkConfig(
        binaries=BinaryLocations(**sparkctl_settings.binaries),
        runtime=SparkRuntimeParams(**sparkctl_settings.runtime),
        compute=ComputeParams(**sparkctl_settings.compute),
    )


def print_settings() -> None:
    """Print the current sparkctl settings."""
    print(sparkctl_settings.to_dict())
