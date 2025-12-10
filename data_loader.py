import pandas as pd
import gspread 
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "supakorn-datawarehouse-199xi-1c7ba182671e.json"
SHEET_ID = "11BH6-8mIp3tuN1YAGi7rC6qAdKUdOnmBaE2UZwLw6VI"
SHEET_NAME = "Month_25"

def load_data ():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    values = sheet.get("A:F")

    header = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows,columns=header)

    df = df.replace("",pd.NA)

    df = df.applymap(lambda x: x.strip() if isinstance(x, str)else x)
    df = df.replace("",pd.NA)

    df = df.dropna(how="all")

    if "Date" in df.columns:
        df = df[~df["Date"].isna()]
    else:
        print("Warning: ไม่พบคอลัมน์ 'Date' ใน DataFrame")

    return df