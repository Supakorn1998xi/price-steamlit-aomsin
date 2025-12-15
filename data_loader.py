# data_loader.py
import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = "11BH6-8mIp3tuN1YAGi7rC6qAdKUdOnmBaE2UZwLw6VI"
SHEET_NAME = "Month_25"

MAIN_RANGE = "A:F"
EXTRA_RANGE = "M2:Q3"
EXTRA_COLS = ["M", "N", "O", "P", "Q"]

# ---------------- AUTH ----------------
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE,
    )
    return gspread.authorize(creds)

# ---------------- DATA LOADER ----------------
@st.cache_data(ttl=300, show_spinner=False)  # cache 5 นาที
def load_data() -> pd.DataFrame:
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    # ---------- Load main table ----------
    values = sheet.get(MAIN_RANGE)

    if not values or len(values) < 2:
        return pd.DataFrame()

    header, *rows = values
    df = pd.DataFrame(rows, columns=header)

    # ---------- Clean data ----------
    df = (
        df.replace("", pd.NA)
          .apply(lambda col: col.str.strip() if col.dtype == "object" else col)
          .dropna(how="all")
    )

    if "Date" in df.columns:
        df = df[df["Date"].notna()]
    else:
        st.warning("⚠️ ไม่พบคอลัมน์ Date")

    df = df.reset_index(drop=True)

    # ---------- Load extra columns (M:Q) ----------
    df_extra = pd.DataFrame([[pd.NA]*5, [pd.NA]*5], columns=EXTRA_COLS)

    try:
        extra_values = sheet.get(EXTRA_RANGE) or []
        while len(extra_values) < 2:
            extra_values.append([""] * 5)

        extra_values = [(r + [""] * 5)[:5] for r in extra_values[:2]]
        df_extra = (
            pd.DataFrame(extra_values, columns=EXTRA_COLS)
              .replace("", pd.NA)
        )
    except Exception as e:
        st.warning(f"⚠️ ดึง M-Q ไม่สำเร็จ: {e}")

    # ---------- Merge ----------
    for col in EXTRA_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    df.loc[0:1, EXTRA_COLS] = df_extra.values

    return df
