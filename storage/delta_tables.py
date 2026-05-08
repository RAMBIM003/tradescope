from pathlib import Path

BASE_DIR = Path("C:/trade/data")

RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
DELTA_DIR = BASE_DIR / "delta"


def write_raw(df, table_name):
    path = str(RAW_DIR / table_name)

    (
        df.write
        .mode("overwrite")
        .parquet(path)
    )

    print(f"[RAW] saved → {path}")


def write_processed(df, table_name):
    path = str(PROCESSED_DIR / table_name)

    (
        df.write
        .mode("overwrite")
        .parquet(path)
    )

    print(f"[PROCESSED] saved → {path}")


def write_delta(df, table_name):
    path = str(DELTA_DIR / table_name)

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(path)
    )

    print(f"[DELTA] saved → {path}")