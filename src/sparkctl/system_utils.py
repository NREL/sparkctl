def make_spark_url(hostname: str) -> str:
    """Return a Spark URL with the hostname."""
    return f"spark://{hostname}:7077"
