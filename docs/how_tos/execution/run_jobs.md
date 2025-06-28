# How to run Spark jobs in Python
These instructions assume that have allocated compute nodes and started a Spark cluster.

For all steps below, set the environment variable `SPARK_CONF_DIR`, pointed at your configuration directory.

```console
$ export SPARK_CONF_DIR=$(pwd)/conf
```
   
## Interactive session with pyspark

1. Start a Spark process.

   If using pyspark:
   ```console
   $ pyspark --master spark://$(hostname):7077
   ```
   
   If using pyspark-client (Spark Connect):
   ```console
   $ python
   >>> from pyspark.sql import SparkSession
   >>> spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
   ```

2. Optional: check your environment to ensure that all configuration settings are correct.
Most importantly, ensure that you connected to the Spark cluster master and are not in local mode.
pyspark prints the connection information during startup. For example:
    ```
    Spark context available as 'sc' (master = spark://r2i7n35:7077, app id = app-20221202224041-0000).
    ```
    You can dump all configuration settings with this command:
    ```
    >>> spark.sparkContext.getConf().getAll()
    ```

3. Create or load dataframes with the global `SparkSession` variable named `spark`:
   ```
   >>> df = spark.read.parquet("my_data.parquet")
   >>> df.show()
   ```

## Jupyter notebook
The command below will allow you to connect to the Spark cluster in a Jupyter notebook.

1. Set these environment variables.

   ```console
   $ export PYSPARK_DRIVER_PYTHON=jupyter
   ```
   ```console
   $ export PYSPARK_DRIVER_PYTHON_OPTS="notebook --no-browser --port=8889 --ip=0.0.0.0"
   ```

2. Start the notebook server

   ```console
   $ pyspark --master spark://$(hostname):7077
   ```
   
   The Jupyter process will print a URL to the terminal. You can access it from your laptop after you forward the ports through an ssh tunnel.
   
   This is a Mac/Linux example. On Windows adjust the environment variable syntax as needed for the Command shell or PowerShell.

   ```console
   $ export COMPUTE_NODE=<your-compute-node-name>
   $ ssh -L 4040:$COMPUTE_NODE:4040 -L 8080:$COMPUTE_NODE:8080 -L 8889:$COMPUTE_NODE:8889 $USER@kestrel.hpc.nrel.gov
   ```

## Script execution with spark-submit
1. Set the environment variable `SPARK_CONF_DIR`, pointed at your configuration directory.

   ```console
   $ export SPARK_CONF_DIR=$(pwd)/conf
   ```

2. Start a Spark process.

   ```console
   $ spark-submit --master spark://$(hostname):7077 my_job.py
   ```

   where `my_job.py` contains this code to connect to Spark:
   
   ```python
   from pyspark.sql import SparkSession
   spark = SparkSession.builder.appName("my_app").getOrCreate()
   ```
