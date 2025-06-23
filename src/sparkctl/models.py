from pathlib import Path
import shutil
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SparkctlBaseModel(BaseModel):
    """Base model for data models in the sparkctl package."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        use_enum_values=False,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )


class BinaryLocations(SparkctlBaseModel):
    """Locations to the Spark and dependent software. Hadoop, Hive, and the PostgreSQL jar file
    are only required if the user wants to enable a Postgres-based Hive metastore.
    """

    spark_path: Path = Field(description="Path to the Spark binaries.")
    hadoop_path: Path | None = Field(default=None, description="Path to the Hadoop binaries.")
    hive_tarball: Path | None = Field(default=None, description="Path to the Hive binaries.")
    postgresql_jar_file: Path | None = Field(
        default=None, description="Path to the PostgreSQL jar file."
    )


class SparkRuntimeParams(SparkctlBaseModel):
    """Controls Spark runtime parameters."""

    executor_cores: int = Field(
        default=5,
        description="Number of cores per executor",
    )
    driver_memory_gb: int = Field(
        default=10,
        description="Driver memory in GB. This is the maximum amount of data that can be pulled "
        "into the application.",
    )
    node_memory_overhead_gb: int = Field(
        default=10,
        description="Memory to reserve for system processes.",
    )
    use_local_storage: bool = Field(
        default=False,
        description="Use compute node local storage for shuffle data.",
    )
    start_connect_server: bool = Field(
        default=False,
        description="Enable the Spark connect server.",
    )
    start_history_server: bool = Field(
        default=False,
        description="Enable the Spark history server.",
    )
    start_thrift_server: bool = Field(
        default=False,
        description="Enable the Thrift server to connect a SQL client.",
    )
    enable_dynamic_allocation: bool = Field(
        default=False,
        description="Enable Spark dynamic resource allocation.",
    )
    shuffle_partition_multiplier: int = Field(
        default=1,
        description="Spark SQL shuffle partition multiplier (multipy by the number of worker CPUs)",
    )
    enable_hive_metastore: bool = Field(
        default=False,
        description="Create a Hive metastore with Spark defaults (Apache Derby). "
        "Supports only one Spark session.",
    )
    enable_postgres_hive_metastore: bool = Field(
        default=False,
        description="Create a metastore with PostgreSQL. Supports multiple Spark sessions.",
    )
    postgres_password: str | None = Field(
        default=None,
        description="Password for PostgreSQL.",
    )

    @field_validator("postgres_password")
    @classmethod
    def set_postgres_password(cls, postgres_password: str | None) -> str:
        if postgres_password is None:
            return str(uuid4())
        return postgres_password


class RuntimeDirectories(SparkctlBaseModel):
    """Defines the directories to be used by a Spark cluster."""

    base: Path = Field(
        default=Path(),
        description="Base directory for the cluster configuration",
    )
    spark_scratch: Path = Field(
        default=Path("spark_scratch"),
        description="Directory to use for shuffle data.",
    )
    metastore_dir: Path = Field(
        default=Path(), description="Set a custom directory for the metastore and warehouse."
    )

    def get_events_dir(self) -> Path:
        """Return the file path to hive-site.xml"""
        return self.get_spark_conf_dir() / "events"

    def get_hive_site_file(self) -> Path:
        """Return the file path to hive-site.xml"""
        return self.get_spark_conf_dir() / "hive-site.xml"

    def get_spark_conf_dir(self) -> Path:
        """Return the Spark conf directory"""
        return (self.base / "conf").absolute()

    def get_spark_defaults_file(self) -> Path:
        """Return the file path to spark-defaults.conf"""
        return self.get_spark_conf_dir() / "spark-defaults.conf"

    def get_spark_env_file(self) -> Path:
        """Return the file path to spark-env.sh"""
        return self.get_spark_conf_dir() / "spark-env.sh"

    def get_spark_log_file(self) -> Path:
        """Return the file path to spark-env.sh"""
        return self.get_spark_conf_dir() / "log4j2.properties"

    def get_workers_file(self) -> Path:
        """Return the file path to workers"""
        return self.get_spark_conf_dir() / "workers"

    def clean_spark_conf_dir(self) -> Path:
        """Ensure that the Spark conf dir exists and is clean."""
        conf_dir = self.get_spark_conf_dir()
        if conf_dir.exists():
            shutil.rmtree(conf_dir)
        conf_dir.mkdir()
        return conf_dir


class ComputeEnvironment(StrEnum):
    """Defines the supported compute environments."""

    LOCAL = "local"
    SLURM = "slurm"


class PostgresScripts(SparkctlBaseModel):
    """Scripts that setup a PostgreSQL database for use in a Hive metastore.
    Relative paths are assumed to be based on the root path of the sparkctl package.
    Absolute paths can be anywhere on the filesystem.
    """

    start_container: str = "postgres/start_container.sh"
    stop_container: str = "postgres/stop_container.sh"
    setup_metastore: str = "postgres/setup_metastore.sh"

    def get_script_path(self, name: str) -> Path:
        """Return the path on the filesystem for the script"""
        path = Path(getattr(self, name))
        if path.is_absolute():
            return path
        return Path(__file__).parent / path


class ComputeParams(SparkctlBaseModel):
    environment: ComputeEnvironment = ComputeEnvironment.SLURM
    postgres: PostgresScripts = PostgresScripts()


class SparkConfig(SparkctlBaseModel):
    """Contains all Spark configuration parameters."""

    binaries: BinaryLocations
    runtime_params: SparkRuntimeParams = SparkRuntimeParams()
    directories: RuntimeDirectories = RuntimeDirectories()
    compute: ComputeParams = ComputeParams()
