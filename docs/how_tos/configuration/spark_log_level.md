# How to set a custom Spark log level
By default, Spark logs messages at the `INFO` level. This can be very verbose when running jobs
through `spark-submit`.

Here's how to reduce the verbosity:

```console
$ sparkctl configure --spark-log-level warn
```
