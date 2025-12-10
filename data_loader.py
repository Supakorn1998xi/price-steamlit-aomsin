import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "11BH6-8mIp3tuN1YAGi7rC6qAdKUdOnmBaE2UZwLw6VI"
SHEET_NAME = "Month_25"

def load_data():
    # โหลด Credential จาก Streamlit Secrets
    sa_info = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        sa_info,
        scopes=SCOPE
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    values = sheet.get("A:F")

    if not values:
        st.error("ไม่พบข้อมูลใน Google Sheet")
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=header)

    # แทนค่าที่ว่างให้เป็น NA
    df = df.replace("", pd.NA)

    # Strip ช่องว่าง
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # ลบแถวที่ไม่มีข้อมูล
    df = df.dropna(how="all")

    # ตรวจสอบคอลัมน์ Date
    if "Date" in df.columns:
        df = df[~df["Date"].isna()]
    else:
        st.warning("⚠️ ไม่พบคอลัมน์ 'Date' ใน DataFrame")

    return df
