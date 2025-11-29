(tutorials)=
# Tutorials

These tutorials guide you through running Spark jobs on HPC clusters using sparkctl. Each tutorial covers a different workflow - choose the one that best fits your needs.

## Which Tutorial Should I Use?

| Tutorial | Best For | Client Install | Interface |
|----------|----------|----------------|-----------|
| [spark-submit / pyspark](run_spark_jobs.md) | Traditional Spark users, production jobs | `sparkctl[pyspark]` (full) | CLI |
| [Spark Connect CLI](run_python_spark_jobs_spark_connect.md) | Lightweight client, remote connectivity | `sparkctl` | CLI |
| [Python Library](run_python_spark_jobs_script.md) | Programmatic control, automation scripts | `sparkctl` | Python |
| [Interactive Development](run_python_spark_jobs_interactively.md) | Exploratory analysis, debugging | `sparkctl` | Python REPL |

### Decision Guide

**Start here if you're new to sparkctl**: [spark-submit / pyspark](run_spark_jobs.md) - this is the most familiar workflow for existing Spark users.

**Choose by use case**:

- **"I want to submit batch jobs"** → [spark-submit / pyspark](run_spark_jobs.md)
- **"I want a minimal client installation"** → [Spark Connect CLI](run_python_spark_jobs_spark_connect.md)
- **"I want to control the cluster from Python code"** → [Python Library](run_python_spark_jobs_script.md)
- **"I want to explore data interactively"** → [Interactive Development](run_python_spark_jobs_interactively.md)

```{eval-rst}
.. toctree::
    :maxdepth: 2
    :caption: Contents:

    run_spark_jobs
    run_python_spark_jobs_spark_connect
    run_python_spark_jobs_script
    run_python_spark_jobs_interactively
```
