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

    values = sheet.get("A1:F50")

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

        # ดึงแค่ 2 แถว

    # ---------------- ดึงเพิ่ม M:Q แค่ 2 แถว (กันพัง 100%) ----------------
    extra_cols = ["M", "N", "O", "P", "Q"]
    df_extra = pd.DataFrame([[pd.NA]*5, [pd.NA]*5], columns=extra_cols)  # ค่า default เสมอ

    try:
        extra_values = sheet.get("M2:Q3")  # 2 rows x 5 cols
        if extra_values:
            # ทำให้มี 2 แถวเสมอ + 5 คอลัมน์เสมอ
            while len(extra_values) < 2:
                extra_values.append([""]*5)
            extra_values = [(row + [""]*5)[:5] for row in extra_values[:2]]

            df_extra = pd.DataFrame(extra_values, columns=extra_cols)
            df_extra = df_extra.replace("", pd.NA)
            df_extra = df_extra.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    except Exception as e:
        st.warning(f"⚠️ ดึงช่วง M2:Q3 ไม่สำเร็จ: {e}")

    # ---------------- เติมค่า M-Q เฉพาะ 2 แถวแรกของ df ----------------
    df_out = df.reset_index(drop=True).copy()
    for c in extra_cols:
        if c not in df_out.columns:
            df_out[c] = pd.NA

    df_out.loc[0:1, extra_cols] = df_extra.values


    return df_out
