# Run jobs on an Spark Cluster on an HPC

In this tutorial you will learn how to start a Spark cluster on HPC compute nodes and then run
Spark jobs with `spark-submit`.

1. Install a Spark client, such as `pyspark`, such that `spark-submit` is available. For example,

   ```console
   $ pip install pyspark
   ```

2. Allocate compute nodes, such as with Slurm. This example acquires 4 CPUs and 30 GB of memory
   for the Spark master process and user application + Spark driver and 2 complete nodes for Spark
   workers.

   ```console
   $ salloc -t 01:00:00 -n4 --partition=shared --mem=30G : -N2 --account=<your-account> --mem=240G
   ```

3. Activate the Python environment that contains sparkctl.

   ```console
   $ module load python
   $ source ~/python-envs/sparkctl
   ```

4. Configure the Spark cluster. The sparkctl code will detect the compute nodes based on
   Slurm environment variables.

   ```console
    $ sparkctl configure
    ```
    
5. Optional, inpect the Spark configuration in `./conf`.
    
6. Start the cluster.

    ```console
    $ sparkctl start
    ```

7. Set the environment variable `SPARK_CONF_DIR`. This will ensure that your application uses the
   Spark settings created in step 2. Instructions will be printed to the console. By default, it
   will be

   ```console
   $ export SPARK_CONF_DIR=$(pwd)/conf
   ```

8. Set the `JAVA_HOME` environment variable to be the same as the java used by Spark. This should
   bin in your `/.sparkctl.toml` configuration file.

   ```console
   $ export JAVA_HOME=/datasets/images/apache_spark/jdk-21.0.7
   ```

9. Run your application. The recommended behavior is to launch your application through
   `spark-submit`:

   ```console
   $ spark-submit --master spark://$(hostname):7077 my-job.py
   ```

10. Optional, create a SparkSession in your own Python script. This is not recommended unless you
   want to set breakpoints inside your code.

   ```console
   $ python my-job.py
   ```

   For this to work, you may need to set the environment variable `PYSPARK_PYTHON` to the path to
   your python executable. Otherwise, the Spark workers may try to use the version of Python
   included in the Spark distribution, which likely won't be compatible.

   ```console
   $ export PYSPARK_PYTHON=$(which python)
   ```

11. Shut down the cluster.

   ```console
   $ sparkctl stop
   ```
