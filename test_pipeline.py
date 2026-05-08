import os
import findspark
import yfinance as yf

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

from storage.delta_tables import (
    write_raw,
    write_processed,
    write_delta
)

findspark.init()

# FORCE WINDOWS PYTHON
os.environ["PYSPARK_PYTHON"] = r"C:\trade\.venv\Scripts\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\trade\.venv\Scripts\python.exe"

builder = (
    SparkSession.builder
    .appName("TradePipeline")
    .master("local[*]")

    # DELTA CONFIG
    .config(
        "spark.jars.packages",
        "io.delta:delta-spark_2.12:3.2.0"
    )
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    )
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    )

    # IMPORTANT
    .config(
        "spark.pyspark.python",
        r"C:\trade\.venv\Scripts\python.exe"
    )
    .config(
        "spark.pyspark.driver.python",
        r"C:\trade\.venv\Scripts\python.exe"
    )
)

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# DOWNLOAD STOCK DATA
df_pd = yf.download("AAPL", period="5d")

df_pd.reset_index(inplace=True)

df_pd.columns = [
    c[0].lower() if isinstance(c, tuple) else c.lower()
    for c in df_pd.columns
]

spark_df = spark.createDataFrame(df_pd)

spark_df.show(5)

# RAW
write_raw(spark_df, "market_prices")

# PROCESSED
processed_df = spark_df.dropna()

write_processed(processed_df, "market_prices_clean")

# DELTA
write_delta(processed_df, "market_prices")

print("Pipeline complete ✔")

spark.stop()