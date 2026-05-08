from pyspark.sql import Row
from storage.delta_tables import get_spark, write_to_delta
from data_ingestion.market_api import fetch_stock_price


def transform_daily_data(symbol: str):
    """
    Fetches stock data and converts it into a clean Spark DataFrame.
    Handles missing or inconsistent API fields safely.
    """

    raw = fetch_stock_price(symbol)

    time_series = raw.get("Time Series (Daily)", {})

    rows = []

    for date, values in time_series.items():

        try:
            rows.append(Row(
                date=date,
                open=float(values.get("1. open", 0)),
                high=float(values.get("2. high", 0)),
                low=float(values.get("3. low", 0)),
                close=float(values.get("4. close", 0)),
                volume=int(values.get("5. volume", 0)),
                symbol=symbol
            ))

        except Exception as e:
            print(f"Skipping {date} due to error: {e}")

    spark = get_spark()
    df = spark.createDataFrame(rows)

    return df