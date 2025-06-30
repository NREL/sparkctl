import pyspark.sql.functions as F
from pyspark.sql import SparkSession


spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
df = spark.createDataFrame([(x, x + 1) for x in range(100)], ["a", "b"])
result = df.agg(F.sum("a").alias("sum_a"), F.sum("b").alias("sum_b")).collect()
assert result[0].sum_b > result[0].sum_a
