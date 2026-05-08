import yfinance as yf
from pyspark.sql import SparkSession


def fetch_market_data(spark: SparkSession, symbol="AAPL", period="5d"):
    data = yf.download(symbol, period=period)

    data.reset_index(inplace=True)

    data.columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    data["symbol"] = symbol

    return spark.createDataFrame(data)