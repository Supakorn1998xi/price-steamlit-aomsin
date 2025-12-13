# home_page.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import calendar


def parse_bath(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and x.strip() == ""):
        return 0.0
    s = str(x).strip()
    s = s.replace("฿", "").replace(",", "")
    try:
        return float(s)
    except:
        return 0.0


def fmt_bath(v: float):
    return f"{v:,.2f} Bath"


def kpi_card(title: str, value: str):
    return f"""
<div class="kpi-card">
  <div class="kpi-title">{title}</div>
  <div class="kpi-value">{value}</div>
</div>
"""


# CSS (บังคับให้การ์ดชนะ theme)
st.markdown(
    """
<style>
.kpi-card{
  border: 1px solid rgba(255,255,255,0.25) !important;
  border-radius: 999px !important;
  padding: 16px 18px !important;
  background: rgba(255,255,255,0.95) !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.15) !important;
  text-align: center !important;
}
.kpi-title{
  font-size: 14px !important;
  color: rgba(0,0,0,0.55) !important;
  margin-bottom: 4px !important;
}
.kpi-value{
  font-size: 26px !important;
  font-weight: 600 !important;
  color: rgba(0,0,0,0.90) !important;
  line-height: 1.1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def render_home(df: pd.DataFrame):
    # ---------------- Header HTML ----------------
    last_update_str = datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%d %b %Y , %H:%M:%S")

    header_html = f"""
<html>
<head>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: 'Prompt', sans-serif;
    }}
  </style>
</head>

<body style="font-family: 'Prompt', sans-serif; margin:0;">

<div style="background-color:#1f1f1f;color:#ffffff;padding:10px 30px;
            display:flex;align-items:center;justify-content:space-between;">

  <div style="display:flex;align-items:center;gap:8px;font-size:20px;font-weight:600;">
    <span style="font-size:28px;">🦖</span>
    <span>Dinosaur Fai .com</span>
  </div>

  <div style="text-align:center;flex:1;font-size:16px;">
    <div style="font-weight:600;">Date</div>
    <div>
      <span id="dateLabel"></span>
      &nbsp;&nbsp;&nbsp;
      <span id="timeLabel"></span>
    </div>
  </div>

  <div style="text-align:right;font-size:12px;">
    <div style="opacity:0.8;">Last Update</div>
    <div>{last_update_str}</div>
  </div>

</div>

<script>
  function pad(n) {{
    return n < 10 ? '0' + n : n;
  }}

  function updateClock() {{
    var now = new Date();
    var day = pad(now.getDate());
    var monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var month = monthNames[now.getMonth()];
    var year = now.getFullYear();
    var weekdayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    var weekday = weekdayNames[now.getDay()];

    var hours = pad(now.getHours());
    var minutes = pad(now.getMinutes());
    var seconds = pad(now.getSeconds());

    document.getElementById('dateLabel').textContent =
        day + " " + month + " " + year + " (" + weekday + ")";
    document.getElementById('timeLabel').textContent =
        "Time " + hours + ":" + minutes + ":" + seconds;
  }}

  updateClock();
  setInterval(updateClock, 1000);
</script>

</body>
</html>
"""
    components.html(header_html, height=78)

    # ---------------- เตรียมข้อมูล Date ----------------
    df_display = df.copy()

    df_display["date_dt"] = pd.to_datetime(
        df_display["Date"],
        dayfirst=True,
        errors="coerce"
    )
    df_display = df_display.dropna(subset=["date_dt"])

    if not df_display.empty:
        min_date = df_display["date_dt"].min().date()
        max_date = df_display["date_dt"].max().date()
    else:
        min_date = max_date = datetime.now(ZoneInfo("Asia/Bangkok")).date()

    # ---------------- UI Filter ----------------
    col_from, col_to, col_type, col_list, col_channel = st.columns([2, 2, 1.5, 1.5, 1.5])

    with col_from:
        st.text("From")
        date_from = st.date_input(
            "from_date",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            label_visibility="collapsed",
        )

    with col_to:
        st.text("To")
        date_to = st.date_input(
            "to_date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            label_visibility="collapsed",
        )

    with col_type:
        st.text("Type")
        type_options = ["All"]
        if "Type" in df_display.columns:
            type_options += sorted(df_display["Type"].dropna().astype(str).unique().tolist())
        selected_type = st.selectbox("type_select", type_options, index=0, label_visibility="collapsed")

    with col_list:
        st.text("List")
        list_options = ["All"]
        if "List" in df_display.columns:
            list_options += sorted(df_display["List"].dropna().astype(str).unique().tolist())
        selected_list = st.selectbox("list_select", list_options, index=0, label_visibility="collapsed")

    with col_channel:
        st.text("Channel")
        channel_options = ["All"]
        if "Channel" in df_display.columns:
            channel_options += sorted(df_display["Channel"].dropna().astype(str).unique().tolist())
        selected_channel = st.selectbox("channel_select", channel_options, index=0, label_visibility="collapsed")

    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # ---------------- Apply Filter ----------------
    mask = (df_display["date_dt"].dt.date >= date_from) & (df_display["date_dt"].dt.date <= date_to)
    df_filtered = df_display.loc[mask].copy()

    if "Type" in df_filtered.columns and selected_type != "All":
        df_filtered = df_filtered[df_filtered["Type"].astype(str) == selected_type]

    if "List" in df_filtered.columns and selected_list != "All":
        df_filtered = df_filtered[df_filtered["List"].astype(str) == selected_list]

    if "Channel" in df_filtered.columns and selected_channel != "All":
        df_filtered = df_filtered[df_filtered["Channel"].astype(str) == selected_channel]

    df_filtered = df_filtered.drop(columns=["date_dt"], errors="ignore")

    st.write("")

    # ---------------- KPI 4 ใบ (อิงเดือนตาม date_to) ----------------
    day_in_month = calendar.monthrange(date_to.year, date_to.month)[1]
    day_passed = date_to.day
    day_left = max(day_in_month - day_passed, 0)
    pct_passed = (day_passed / day_in_month) * 100 if day_in_month else 0.0

    c1, c2, c3, c4 = st.columns(4, gap="large")
    with c1:
        st.markdown(kpi_card("Date of the month", f"{day_in_month} Days"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Date Pass", f"{day_passed} Days"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Balance Date", f"{day_left} Days"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Date Time Passed", f"{pct_passed:.2f}%"), unsafe_allow_html=True)

    st.write("")

    # ---------------- KPI 6 ใบ (คำนวณจาก M:Q) ----------------
    mq = ["M", "N", "O", "P", "Q"]

    if all(c in df_filtered.columns for c in mq):
        tmp = df_filtered[mq].replace("", pd.NA).dropna(how="all")
        if not tmp.empty:
            r = tmp.iloc[0]

            income = parse_bath(r["M"])
            usable_income = parse_bath(r["O"])
            expenses = parse_bath(r["P"])
            balance = parse_bath(r["Q"])

            # จำนวนวันในช่วงที่เลือก (inclusive) สำหรับค่าเฉลี่ยต่อวัน
            days_in_range = max((date_to - date_from).days + 1, 1)

            avg_pay_day = income / days_in_range
            balance_use_pay_day = usable_income / days_in_range

            # ✅ 1 Day Forecast = คงเหลือต่อวัน (เงินคงเหลือ / วันเหลือ)
            one_day_forecast = (balance / day_left) if day_left > 0 else 0.0

            a1, a2, a3, a4, a5, a6 = st.columns(6, gap="large")
            with a1:
                st.markdown(kpi_card("Average Pay : Day", fmt_bath(avg_pay_day)), unsafe_allow_html=True)
            with a2:
                st.markdown(kpi_card("Balance Use Pay : Day", fmt_bath(balance_use_pay_day)), unsafe_allow_html=True)
            with a3:
                st.markdown(kpi_card("1 Day Forecast", fmt_bath(one_day_forecast)), unsafe_allow_html=True)
            with a4:
                st.markdown(kpi_card("Usable Income", fmt_bath(usable_income)), unsafe_allow_html=True)
            with a5:
                st.markdown(kpi_card("Expenses", fmt_bath(expenses)), unsafe_allow_html=True)
            with a6:
                st.markdown(kpi_card("Balance", fmt_bath(balance)), unsafe_allow_html=True)

            st.write("")
        else:
            st.info("ไม่พบข้อมูลในคอลัมน์ M-Q สำหรับคำนวณ KPI")
    else:
        st.info("ยังไม่พบคอลัมน์ M-Q ในข้อมูล (ตรวจ data_loader ว่าดึงมาแล้ว)")

    # ---------------- ตาราง ----------------
    st.subheader(f"ข้อมูลหลัง Filter (จำนวน {len(df_filtered)} แถว)")
    st.dataframe(df_filtered, use_container_width=True)
