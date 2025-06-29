# Run Python jobs on an Spark Cluster on an HPC

In this tutorial you will learn how to start a Spark cluster on HPC compute nodes and then run
Spark jobs in Python through `pyspark-client`.

1. Allocate compute nodes, such as with Slurm. This example acquires 4 CPUs and 30 GB of memory
   for the Spark master process and user application + Spark driver and 2 complete nodes for Spark
   workers.

   ```console
   $ salloc -t 01:00:00 -n4 --partition=shared --mem=30G : -N2 --account=<your-account> --mem=240G
   ```

2. Activate the Python environment that contains sparkctl.

   ```console
   $ module load python
   $ source ~/python-envs/sparkctl
   ```

3. Edit the sparkctl configuration that you previously created. By default, it is
   `~/.sparkctl.toml.` Alternatively, you can copy and modify the config file, and then pass its
   path to the next command.
   
4. Start the Spark cluster. This command will detect the compute nodes based on Slurm environment,
   configure and start a Spark cluster, then return a `SparkSession`.

   ```console
    $ python
    ```
    
   ```python
   from sparkctl import ClusterManager
   mgr = ClusterManager.start_from_config_file()
   spark = mgr.get_spark_session()
   df = spark.createDataFrame([(x, x + 1) for x in range(1000)], ["a","b"])
   df.show(n=5)
   ```
   ```console
   +---+---+
   |  a|  b|
   +---+---+
   |  0|  1|
   |  1|  2|
   |  2|  3|
   |  3|  4|
   |  4|  5|
   +---+---+
   only showing top 5 rows 
   ```

5. Shut down the cluster.

   ```python
   mgr.stop()
   ```
