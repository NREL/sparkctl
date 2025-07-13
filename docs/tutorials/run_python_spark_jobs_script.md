# Run Python jobs on an Spark Cluster on an HPC in a script

In this tutorial you will learn how to start a Spark cluster on HPC compute nodes and then run
Spark jobs in Python through `pyspark-client` with the Spark Connect Server in a script.

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

3. Add the code below to a Python script. This code block will configure and start the Spark
   cluster, run your Spark job, and then stop the cluster.

   ```python
   from sparkctl import ClusterManager, make_default_spark_config
   
   # This loads your global sparkctl configuration file (~/.sparkctl.toml).
   config = make_default_spark_config()
   # Set runtime options as desired.
   # config.runtime.driver_memory_gb = 20
   # config.runtime.use_local_storage = True
   mgr = ClusterManager(config)
   with mgr.managed_cluster() as spark:
       df = spark.createDataFrame([(x, x + 1) for x in range(1000)], ["a","b"])
       df.show(n=5)
