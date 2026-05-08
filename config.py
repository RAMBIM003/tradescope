import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

BASE_URL = "https://www.alphavantage.co/query"
DELTA_PATH = "data/delta_lake"
APP_NAME = "TradeRiskSystem"


RAW_PATH = r"C:\trade\data\raw"
PROCESSED_PATH = r"C:\trade\data\processed"
DELTA_PATH = r"C:\trade\data\delta"
