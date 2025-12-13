# data_loader.py
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


@st.cache_data(ttl=300)  # cache 5 นาที
def load_data():
    sa_info = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        sa_info,
        scopes=SCOPE
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    values = sheet.get("A:F")

    if not values or len(values) < 2:
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=header)

    # Clean data
    df = df.replace("", pd.NA)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.dropna(how="all")

    # Ensure Date exists
    if "Date" in df.columns:
        df = df[~df["Date"].isna()]
    else:
        st.warning("⚠️ ไม่พบคอลัมน์ Date")

    # ---------- ดึง M:Q (2 แถวเสมอ) ----------
    extra_cols = ["M", "N", "O", "P", "Q"]
    df_extra = pd.DataFrame([[pd.NA]*5, [pd.NA]*5], columns=extra_cols)

    try:
        extra_values = sheet.get("M2:Q3")
        if extra_values:
            while len(extra_values) < 2:
                extra_values.append([""] * 5)
            extra_values = [(r + [""]*5)[:5] for r in extra_values[:2]]
            df_extra = pd.DataFrame(extra_values, columns=extra_cols)
            df_extra = df_extra.replace("", pd.NA)
    except Exception as e:
        st.warning(f"⚠️ ดึง M-Q ไม่สำเร็จ: {e}")

    df_out = df.reset_index(drop=True).copy()

    for c in extra_cols:
        if c not in df_out.columns:
            df_out[c] = pd.NA

    df_out.loc[0:1, extra_cols] = df_extra.values

    return df_out
