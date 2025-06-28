# sparkctl
This package extends the Apache Spark launcher scripts to support ephemeral clusters on HPC
compute nodes.


## Compute Nodes

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

4. Run jobs as described [below](#run-jobs).



## Apache Hive

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
