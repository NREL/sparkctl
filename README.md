# sparkctl
This package extends the Apache Spark launcher scripts to support ephemeral clusters on HPC
compute nodes.

## Prerequisites
The package requires that you download Apache Spark, a supported version of Java, and optional
dependencies.

Download and extract these tarballs to a directory accessible on all compute nodes:

- https://dlcdn.apache.org/spark/spark-4.0.0/spark-4.0.0-bin-hadoop3.tgz
- https://download.java.net/java/GA/jdk21.0.1/415e3f918a1f4062a0074a2794853d0d/12/GPL/openjdk-21.0.1_linux-x64_bin.tar.gz

If running on a Mac, download this version of Java instead:

- https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/openjdk-21.0.2_macos-aarch64_bin.tar.gz

Download these packages if you will be using a PostgreSQL-based Hive metastore. Extract
Hadoop but not Hive.

- https://archive.apache.org/dist/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
- https://downloads.apache.org/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
- https://jdbc.postgresql.org/download/postgresql-42.7.4.jar

## Installation
Create and activate a Python virtual environment (or optionally use an existing environment).

```console
$ python -m venv ~/python-envs/sparkctl
```

```console
$ source ~/python-envs/sparkctl/bin/activate
```

```console
$ pip install git+https://github.nrel.gov:dthom/sparkctl.git
```

### One-time setup
These instructions assume you are in Slurm HPC environment. Adjust accordingly.

If using Spark only:
```console
sparkctl default-config -e slurm <path-to-apache-spark> <path-to-java>
```

If using a PostgreSQL-based Hive metastore:
```console
sparkctl default-config -e slurm <path-to-apache-spark> \
    --hadoop-path <path-to-extracted-hadoop-directory> \
    --hive-tarball <path-to-hive-tarball> \
    --postgresql-jar-file <path-to-postgres-file>
```

## Compute Nodes
Consider the type of compute nodes to acquire.

If you will be performing large shuffles then you should prefer nodes with fast local
storage. A minimum requirement is approximately 500 MB/s. Drives that can deliver 2 GB/s
are ideal.

- Any modern SSD should be sufficient.
- A spinning disk will be too slow.
- An HPC shared filesystem (e.g., Lustre) will be slower than an SSD, but is likely sufficient.
- A RAM drive (`/dev/shm`) will work well for smaller data sizes. Many HPC compute nodes have these.
- If the size of the data to be shuffled is greater than the size of the nodes' SSDs, then
you'll need to either add more nodes or use the shared filesystem.

## Basic Configuration Instructions
This section lists instructions that should be sufficient for most cases. Refer to [Advanced
Instructions](#advanced-instructions) to customize the Spark configuration parameters.

**Notes**:

- These scripts require that the Slurm allocation(s) for Spark workers use all resources
in the nodes and that all nodes have the same number of CPUs.
- All Slurm allocations must request memory and not rely on default values. The scripts
rely on a Slurm environment variable which is only set when the user passes `--mem`.

1. Acquire interactive compute nodes. Here are examples using the `debug` partition on Kestrel
with ideal node types. Note that you may want to consider
[heterogeneous jobs](#heterogeneous-slurm-jobs) and [compute node failures](#compute-node-failures).

    ```
    $ salloc -t 01:00:00 -N2 --account=<your-account> --partition=debug --mem=240G -C lbw
    ```

2. Configure and start the cluster. Run the command with `--help` to see all options.

    This example assumes that you were automatically logged into the first compute node in your
    allocation by `salloc` and the environment variable `SLURM_JOB_ID` is set.
    
    ```console
    $ sparkctl configure-and-start
    ```

    Use the compute nodes' in-memory tmpfs (valid on Kestrel):
    ```console
    $ sparkctl configure-and-start --spark-scratch /dev/shm/spark-scratch
    ```

    Use custom location on the shared filesystem:
    ```console
    $ sparkctl configure-and-start --spark-scratch /scratch/$USER/spark-scratch
    ```

    **Note**: This command creates several directories that are used by the cluster. If you will
    run multiple clusters simultaneously, be sure to use different base directories. The base
    directory is the current directory by default, and can be changed with `--directory`.


3. Set this environment variable so that your jobs use the Spark configuration settings that you
just created.
    ```console
    $ export SPARK_CONF_DIR=$(pwd)/conf
    ```

4. Run jobs as described [below](#run-jobs).

### Heterogeneous Slurm jobs
The scripts in this package are well-suited for an environment where the
Spark cluster manager, driver, and user application run on a shared node with a limited number of
CPUs, and the workers run on exclusive nodes with uniform resources. Refer to this
[diagram](https://spark.apache.org/docs/latest/cluster-overview.html) to see an illustration
of the Spark cluster components.

This can be achieved with
[Slurm heterogeneous jobs](https://slurm.schedmd.com/heterogeneous_jobs.html).

Here is one possible configuration:
- Spark driver memory = 10 GB
- Spark master memory + overhead for OS and Slurm = 20 GB
- CPUs for Spark master, driver, user application, and overhead for OS and Slurm = 4

Allocate one compute node from the shared partition and then four from the regular partition.

**Note**: The shared partition must be first and must have only one compute node.
That is where your application will run.

```
$ salloc --account=<your-account> -t 01:00:00 -n4 --mem=30G --partition=shared : \
    -N2 --partition=debug --mem=240G -C lbw
```

Here is the format of sbatch script:
```bash
#!/bin/bash
#SBATCH --account=<my-account>
#SBATCH --job-name=my-job
#SBATCH --time=1:00:00
#SBATCH --output=output_%j.o
#SBATCH --error=output_%j.e
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --mem=30G
#SBATCH --ntasks=4
#SBATCH hetjob
#SBATCH --nodes=2
#SBATCH --mem=240G
#SBATCH --constraint=lbw
```

You will need to adjust the CPU and memory parameters based on what you will pass to
`configure_and_start_spark.sh`.

Then proceed with the rest of the instructions.

### Compute Node Failures
If your job uses multiple compute nodes, you may want to consider setting the flag `--no-kill` in
your `sbatch` command.

By default, if a compute node fails (kernel panic, hardware failure, etc.), Slurm will terminate
the job.

This behavior can be advantageous for a Spark cluster because it can tolerate worker node
failures in many cases. If a job is almost complete when a failure occurs, it may be able to retry
the failed tasks on a different node and complete successfully.

On the other hand, if the remaining nodes will not be able to complete the job, the default
behavior is better.

The more nodes you have, the more likely it is to be beneficial to set this option. If you allocate
two nodes, you probably don't want to set it. If you allocate eight nodes, it may be good to set
it.

Recommendation: only set this option in conjunction with heterogeneous Slurm jobs as discussed
above. The Spark cluster master created by these scripts is not redundant. If it fails, the job
will never complete. Hopefully, since it is doing far less work, it will be less likely to fail.
However, if you are using a shared node, you obviously cannot control what others are doing.

## Apache Hive
Spark supports reading and writing data from [Apache Hive](https://hive.apache.org) as described
[here](https://spark.apache.org/docs/latest/sql-data-sources-hive-tables.html).

This is useful if you want to access data in SQL tables through a JDBC/ODBC client
instead of Parquet files through Python/R or `spark-sql`. It also provides access to Spark with
[SQLAlchemy](https://www.sqlalchemy.org) through
[PyHive](https://kyuubi.readthedocs.io/en/v1.8.0/client/python/pyhive.html).

You can configure Spark with a Hive Metastore by running this command:
```
$ configure_and_start_spark.sh --hive-metastore --metastore-dir /path/to/my/metastore
```

By default Spark uses [Apache Derby](https://db.apache.org/derby/) as the database for the metastore.
This has a limitation: only one client can be connected to the metastore at a time.

If you need multiple simultaneous connections to the metastore, you can use
[PostgreSQL](https://www.postgresql.org) as the backend instead by running the following command:
```
$ configure_and_start_spark.sh --postgers-hive-metastore --metastore-dir /path/to/my/metastore
```
This takes a few extra minutes to start the first time, as it has to download a container and
start the server. Apptainer will cache the container image and you can reuse the database data
across Slurm allocations.

**Note**: The metadata about your tables will be stored in Derby or Postgres. Your tables will
be stored on the filesystem (Parquet files by default) in a directory called `spark_warehouse`,
which gets created in the directory passed to `--metastore-dir` (current directory by default).
Postgres data, if enabled, will be in the same directory (`pg-data`).

## Run Jobs
These instructions assume that have allocated compute nodes and started a Spark cluster.

### Manual mode

1. Install `pyspark` or `pyspark-client` (for [Spark Connect]
(https://spark.apache.org/docs/4.0.0/api/python/getting_started/quickstart_connect.html)) into a Python
virtual environment.

   **Note**: You need to use the same version as the version of your Spark software.

   ```
   $ pip install pyspark==4.0.0
   ```

2. Set the environment variable `SPARK_CONF_DIR`.

   ```
   $ export SPARK_CONF_DIR=$(pwd)/conf
   ```

3. Start a Spark process.

   ```
   $ pyspark --master spark://$(hostname):7077
   ```

4. Optional: check your environment to ensure that all configuration settings are correct.
Most importantly, ensure that you connected to the Spark cluster master and are not in local mode.
pyspark prints the connection information during startup. For example:
    ```
    Spark context available as 'sc' (master = spark://r2i7n35:7077, app id = app-20221202224041-0000).
    ```
    You can dump all configuration settings with this command:
    ```
    >>> spark.sparkContext.getConf().getAll()
    ```

5. Create or load dataframes with the global `SparkSession` variable named `spark`:
   ```
   >>> df = spark.read.parquet("my_data.parquet")
   >>> df.show()
   ```

### Shut down the cluster
This command will stop the Spark processes and the containers.
```console
$ sparkctl stop
```
