# home_page.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import calendar


def render_home(df: pd.DataFrame):

    # ---------- HEADER ----------
    last_update = datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%d %b %Y %H:%M:%S")

    components.html(
        f"""
        <div style="background:#1f1f1f;color:white;padding:10px 30px;
                    display:flex;justify-content:space-between;align-items:center;">
            <div style="font-size:20px;font-weight:600;">🦖 Dinosaur Fai .com</div>
            <div style="font-size:12px;">Last update: {last_update}</div>
        </div>
        """,
        height=60
    )

    if df.empty:
        st.warning("⚠️ ไม่พบข้อมูล")
        return

    # ---------- Spinner ตอนประมวลผล ----------
    with st.spinner("📊 Calculating dashboard..."):

        df_display = df.copy()
        df_display["date_dt"] = pd.to_datetime(
            df_display["Date"],
            dayfirst=True,
            errors="coerce"
        )
        df_display = df_display.dropna(subset=["date_dt"])

        min_date = df_display["date_dt"].min().date()
        max_date = df_display["date_dt"].max().date()

        # ---------- Filter ----------
        c1, c2 = st.columns(2)
        with c1:
            date_from = st.date_input("From", min_date, min_date, max_date)
        with c2:
            date_to = st.date_input("To", max_date, min_date, max_date)

        if date_from > date_to:
            date_from, date_to = date_to, date_from

        mask = (
            (df_display["date_dt"].dt.date >= date_from) &
            (df_display["date_dt"].dt.date <= date_to)
        )
        df_filtered = df_display.loc[mask]

        # ---------- KPI ----------
        day_in_month = calendar.monthrange(date_to.year, date_to.month)[1]
        day_passed = date_to.day
        day_left = day_in_month - day_passed

        k1, k2, k3 = st.columns(3)
        k1.metric("Days in month", day_in_month)
        k2.metric("Days passed", day_passed)
        k3.metric("Days left", day_left)

        # ---------- Table ----------
        st.subheader(f"📋 Data ({len(df_filtered)} rows)")
        st.dataframe(df_filtered, use_container_width=True)
