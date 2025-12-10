# home_page.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd


def render_home(df):
    # ---------------- Header HTML (ฟอนต์ Prompt + เวลา realtime) ----------------
    last_update_str = datetime.now().strftime("%d %b %Y , %H:%M:%S")

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

  <!-- ซ้าย -->
  <div style="display:flex;align-items:center;gap:8px;font-size:20px;font-weight:600;">
    <span style="font-size:28px;">🦖</span>
    <span>Dinosaur Fai .com</span>
  </div>

  <!-- กลาง -->
  <div style="text-align:center;flex:1;font-size:16px;">
    <div style="font-weight:600;">Date</div>
    <div>
      <span id="dateLabel"></span>
      &nbsp;&nbsp;&nbsp;
      <span id="timeLabel"></span>
    </div>
  </div>

  <!-- ขวา -->
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

    components.html(header_html, height=95)

    #st.write("")  # เว้นระยะจากหัว

        # ---------------- เตรียมข้อมูล Date (คอลัมชื่อ Date, รูปแบบวัน/เดือน/ปี) ----------------
    df_display = df.copy()

    # แปลงคอลัม Date -> datetime (ข้อมูล dd/MM/yyyy)
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
        min_date = max_date = datetime.now().date()

    # ---------------- UI Filter: Date From / To + Type + List + Channel ----------------
    #st.caption("Date (DD/MM/YYYY)")

    col_from, col_to, col_type, col_list, col_channel = st.columns([2, 2, 1.5, 1.5, 1.5])

    # From
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

    # To
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

    # Type dropdown
    with col_type:
        st.text("Type")
        if "Type" in df_display.columns:
            type_options = ["All"] + sorted(
                df_display["Type"].dropna().astype(str).unique().tolist()
            )
        else:
            type_options = ["All"]

        selected_type = st.selectbox(
            "type_select",
            type_options,
            index=0,
            label_visibility="collapsed",
        )

    # List dropdown
    with col_list:
        st.text("List")
        if "List" in df_display.columns:
            list_options = ["All"] + sorted(
                df_display["List"].dropna().astype(str).unique().tolist()
            )
        else:
            list_options = ["All"]

        selected_list = st.selectbox(
            "list_select",
            list_options,
            index=0,
            label_visibility="collapsed",
        )

    # Channel dropdown
    with col_channel:
        st.text("Channel")
        if "Channel" in df_display.columns:
            channel_options = ["All"] + sorted(
                df_display["Channel"].dropna().astype(str).unique().tolist()
            )
        else:
            channel_options = ["All"]

        selected_channel = st.selectbox(
            "channel_select",
            channel_options,
            index=0,
            label_visibility="collapsed",
        )

    # ถ้า user เลือกสลับ from/to ก็สลับกลับให้
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    # ---------------- Apply Filter ----------------
    # filter ตามวันที่ก่อน
    mask = (
        (df_display["date_dt"].dt.date >= date_from) &
        (df_display["date_dt"].dt.date <= date_to)
    )
    df_filtered = df_display[mask].copy()

    # filter ตาม Type
    if "Type" in df_filtered.columns and selected_type != "All":
        df_filtered = df_filtered[df_filtered["Type"].astype(str) == selected_type]

    # filter ตาม List
    if "List" in df_filtered.columns and selected_list != "All":
        df_filtered = df_filtered[df_filtered["List"].astype(str) == selected_list]

    # filter ตาม Channel
    if "Channel" in df_filtered.columns and selected_channel != "All":
        df_filtered = df_filtered[df_filtered["Channel"].astype(str) == selected_channel]

    # ลบคอลัมน์ช่วย
    df_filtered = df_filtered.drop(columns=["date_dt"])

    # ---------------- แสดงผล ----------------
    st.subheader(f"ข้อมูลหลัง Filter (จำนวน {len(df_filtered)} แถว)")
    st.dataframe(df_filtered, use_container_width=True)

