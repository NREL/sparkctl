# Debugging

## Spark web UI
The web UI is a good first place to look for problems. Connect to ports 8080 and 4040 on the nodes
running Spark. You may need to create an ssh tunnel. This is an example that creates a tunnel
between a user's Mac laptop and NREL's Kestrel HPC:

```console
$ export COMPUTE_NODE=<your-compute-node-name>
$ ssh -L 4040:$COMPUTE_NODE:4040 -L 8080:$COMPUTE_NODE:8080 $USER@kestrel.hpc.nrel.gov
```

Open your browser to http://localhost:4040 after configuring the tunnel to access the web UI.

## Log files
sparkctl configures Spark to record log files in the base directory. Spark master, worker, and
history logs will be in `./spark_scratch/logs`. Executor logs will be in `./spark_scratch/worker` 
(look for `stderr` files).

## Performance monitoring
If your job is running slowly, check CPU utilization on your compute nodes.

Here is an example of how to run htop on multiple nodes simulataneously with `tmux`.

Download this [script](https://raw.githubusercontent.com/johnko/ssh-multi/master/bin/ssh-multi)

Run it like this:

```console
$ ./ssh-multi node1 node2 nodeN
```
It will start tmux with one pane for each node and synchonize mode enabled. Typing in one pane types
everywhere.

$ htop

```{eval-rst}
.. note:: The file `./conf/workers` contains the node names in your cluster.
```

### Spark tuning resources
- Spark tuning guide from Apache: https://spark.apache.org/docs/latest/tuning.html
- Spark tuning guide from Amazon: https://aws.amazon.com/blogs/big-data/best-practices-for-successfully-managing-memory-for-apache-spark-applications-on-amazon-emr/
- Performance recommendations: https://www.youtube.com/watch?v=daXEp4HmS-E&t=4251s
