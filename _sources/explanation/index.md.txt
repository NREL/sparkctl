(explanation)=
# Explanation

## Spark Cluster Overview
This Spark [documentation page](https://spark.apache.org/docs/latest/cluster-overview.html) gives
an overview of how Spark operates.

## Cluster Mode
sparkctl always configures Spark clusters in
[standalone mode](https://spark.apache.org/docs/latest/spark-standalone.html). Given that sparkctl
expects clusters to be ephemeral, the greater sophistication of YARN and Kubernetes cluster managers
is not required.

## Submitting Applications
Please refer to this [documentation page](https://spark.apache.org/docs/latest/submitting-applications.html)
for Spark's guidance on submitting applications.

To get all submission tools in a Python environment, install pyspark as follows:
```console
$ pip install pyspark
```

Clients for other languages are available at the main Spark
[downloads page](https://spark.apache.org/downloads.html)

## Spark Connect
Spark Connect is a relatively new feature that simplifies client installation and configuration.
Please refer to Spark's [documentation](https://spark.apache.org/docs/latest/spark-connect-overview.html)
for details. If you want to configure and start a Spark cluster, and then connect to it, all within
one Python session, this is the recommended workflow.

Note that there are some caveats listed
[here](https://spark.apache.org/docs/latest/spark-connect-overview.html#how-spark-connect-client-applications-differ-from-classic-spark-applications).

You enable the Spark connect server with this sparkctl command:
```console
$ sparkctl configure --connect-server
```

To install the only the client for Python:
```console
$ pip install pyspark-client
```
