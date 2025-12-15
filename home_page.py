# home_page.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import calendar
import plotly.graph_objects as go
import numpy as np

def build_list_summary_table(df: pd.DataFrame):
    if df.empty or "List" not in df.columns or "Price" not in df.columns:
        return None

    d = df.copy()

    # แปลง Price เป็นตัวเลข
    d["Price_num"] = (
        d["Price"]
        .astype(str)
        .str.replace("฿", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    d["Price_num"] = pd.to_numeric(d["Price_num"], errors="coerce")
    d = d.dropna(subset=["Price_num"])

    if d.empty:
        return None

    # group by List
    summary = (
        d.groupby("List", as_index=False)
        .agg(
            Record_Count=("Price_num", "count"),
            Total=("Price_num", "sum"),
        )
    )

    summary["Average_Pay"] = summary["Total"] / summary["Record_Count"]

    grand_total = summary["Total"].sum()
    summary["Percent"] = summary["Total"] / grand_total * 100

    summary = summary.sort_values("Total", ascending=False)

    # ===== footer =====
    total_count = summary["Record_Count"].sum()
    total_sum = summary["Total"].sum()
    total_avg = total_sum / total_count if total_count > 0 else 0

    footer = pd.DataFrame([{
        "List": "Total",
        "Record_Count": total_count,
        "Total": total_sum,
        "Average_Pay": total_avg,
        "Percent": 100.0
    }])

    summary = pd.concat([summary, footer], ignore_index=True)

    # เพิ่ม Index
    summary.insert(0, "Index", range(1, len(summary) + 1))

    return summary

def render_summary_table_with_sticky_footer(summary_df: pd.DataFrame):
    if summary_df is None or summary_df.empty:
        st.info("ไม่มีข้อมูลสำหรับแสดงตาราง")
        return

    body = summary_df.iloc[:-1].copy()
    footer = summary_df.iloc[-1:].copy()

    html = """
    <style>
    .table-wrap{
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 12px;
      background: rgba(255,255,255,0.06);
      overflow: hidden;
    }
    .table-scroll{
      max-height: 420px;
      overflow-y: auto;
    }
    table{
      width: 100%;
      border-collapse: collapse;
      font-family: 'Prompt', sans-serif;
    }
    thead th{
      position: sticky;
      top: 0;
      background: rgba(20,20,20,0.95);
      color: #fff;
      padding: 10px;
      text-align: left;
    }
    tbody td{
      padding: 10px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      color: rgba(255,255,255,0.9);
    }
    tfoot td{
      position: sticky;
      bottom: 0;
      background: rgba(20,20,20,0.95);
      color: #fff;
      padding: 10px;
      font-weight: 600;
      border-top: 1px solid rgba(255,255,255,0.2);
    }
    .right{ text-align: right; }
    </style>

    <div class="table-wrap">
      <div class="table-scroll">
        <table>
          <thead><tr>
    """

    # ---------- header ----------
    for c in summary_df.columns:
        html += f"<th>{c}</th>"
    html += "</tr></thead><tbody>"

    # ---------- body ----------
    for _, row in body.iterrows():
        html += "<tr>"
        for c in summary_df.columns:
            val = row[c]

            if c == "Average_Pay":
                val = f"{float(val):,.2f}"
            elif c == "Percent":
                val = f"{float(val):.2f}%"

            cls = "right" if c != "List" else ""
            html += f'<td class="{cls}">{val}</td>'
        html += "</tr>"

    html += "</tbody><tfoot><tr>"

    # ---------- footer ----------
    footer_row = footer.iloc[0]
    for c in summary_df.columns:
        val = footer_row[c]

        if c == "Average_Pay":
            val = f"{float(val):,.2f}"
        elif c == "Percent":
            val = f"{float(val):.2f}%"

        cls = "right" if c != "List" else ""
        html += f'<td class="{cls}">{val}</td>'

    html += """
        </tr></tfoot>
        </table>
      </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)




def render_price_trend_chart(df: pd.DataFrame, date_col="Date", price_col="Price"):
    if df is None or df.empty:
        st.info("ยังไม่มีข้อมูลสำหรับกราฟ")
        return

    if date_col not in df.columns or price_col not in df.columns:
        st.info(f"ยังไม่มีข้อมูลสำหรับกราฟ (ตรวจชื่อคอลัมน์ {date_col}/{price_col})")
        st.write("COLUMNS:", df.columns.tolist())
        return

    d = df.copy()

    # ----- date -----
    d["__date"] = pd.to_datetime(d[date_col], dayfirst=True, errors="coerce").dt.date
    d = d.dropna(subset=["__date"])

    # ----- price -----
    # รองรับค่าแบบ: 12,345 | ฿12,345.00 | " 123 " | ฯลฯ
    d["__price"] = (
        d[price_col]
        .astype(str)
        .str.replace("฿", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    d["__price"] = pd.to_numeric(d["__price"], errors="coerce")
    d = d.dropna(subset=["__price"])

    if d.empty:
        st.info("ไม่มีข้อมูลราคา (Price) ที่แปลงเป็นตัวเลขได้ในช่วงที่เลือก")
        return

    # ----- aggregate รายวัน -----
    daily = (
        d.groupby("__date", as_index=False)["__price"]
        .sum()
        .sort_values("__date")
    )

    if daily.empty:
        st.info("ไม่มีข้อมูลกราฟรายวัน")
        return

    x = pd.to_datetime(daily["__date"])
    y = daily["__price"].astype(float).to_numpy()

    avg = float(np.mean(y))
    mx = float(np.max(y))
    mn = float(np.min(y))

    # trend line
    xi = np.arange(len(y))
    if len(y) >= 2:
        m, b = np.polyfit(xi, y, 1)
        trend = m * xi + b
    else:
        trend = y

    fig = go.Figure()

    fig.add_trace(go.Scatter(
    x=x, y=y,
    mode="lines+markers",
    text=[f"{v:,.0f}" for v in y],
    textposition="top center",
    name="Price",
    line=dict(shape="spline", smoothing=1.2)  # ✅ โค้งมนนุ่ม ๆ
))


    fig.add_trace(go.Scatter(
    x=x, y=trend,
    mode="lines",
    name="Trend",
    line=dict(dash="dash", shape="spline", smoothing=1.2)
))


    # avg / max / min lines (กำหนดสี)
    fig.add_hline(
        y=mx,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Max: {mx:,.2f}",
        annotation_position="top left"
    )

    fig.add_hline(
        y=avg,
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Average: {avg:,.2f}",
        annotation_position="bottom left"
    )

    fig.add_hline(
        y=mn,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Min: {mn:,.2f}",
        annotation_position="bottom left"
    )

    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        yaxis=dict(domain=[0.12, 1.0])
    )

    y_padding = (mx - mn) * 0.05
    fig.update_yaxes(range=[mn - y_padding, mx + y_padding])

    fig.update_xaxes(
        type="date",
        tickformat="%d %b %Y",
        ticklabelstandoff=8,
        ticks="outside",
        ticklabelposition="outside"
    )



    st.plotly_chart(fig, use_container_width=True)

def parse_bath(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and x.strip() == ""):
        return 0.0
    s = str(x).strip().replace("฿", "").replace(",", "")
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


def render_home(df: pd.DataFrame):
    # ---------------- KPI CSS (ให้เสถียรทุกครั้งที่ rerun) ----------------

    st.markdown("""
    <style>
    div[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 12px;
    padding: 12px;
    background: rgba(255,255,255,0.06);
    overflow: hidden;
}
    .chart-card [data-testid="stPlotlyChart"]{
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    }
       

    .chart-card{
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 12px;
    padding: 12px;
    background: rgba(255,255,255,0.06);
    overflow: hidden;  /* ✅ กันมุมกราฟโผล่ */
    }

    /* ✅ ตัด padding/กรอบภายในของ Streamlit/Plotly */
    .chart-card .stPlotlyChart, 
    .chart-card iframe {
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)



    st.markdown("""
    <style>
    .kpi-card{
      border: 1px solid rgba(255,255,255,0.18) !important;
      border-radius: 12px !important;
      padding: 12px 14px !important;
      background: rgba(255,255,255,0.06) !important;
      box-shadow: none !important;

      text-align: center !important;
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
      justify-content: center !important;
    }
    .kpi-title{
      font-size: 14px !important;
      font-weight: 400 !important;
      color: rgba(255,255,255,0.85) !important;
      margin-bottom: 6px !important;
    }
    .kpi-value{
      font-size: 22px !important;
      font-weight: 400 !important;
      color: #ffffff !important;
      line-height: 1.2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

    /* ✅ Dino animation */
    .dino{{
      font-size: 28px;
      display: inline-block;
      transform-origin: 50% 100%;
      animation: dino-bounce 1.2s ease-in-out infinite;
      margin-right: 6px;
    }}

    @keyframes dino-bounce{{
      0%, 100% {{ transform: translateY(0) rotate(0deg); }}
      25%      {{ transform: translateY(-2px) rotate(-6deg); }}
      50%      {{ transform: translateY(0) rotate(0deg); }}
      75%      {{ transform: translateY(-2px) rotate(6deg); }}
    }}
  </style>
</head>

<body style="font-family: 'Prompt', sans-serif; margin:0;">

<div style="background-color:#1f1f1f;color:#ffffff;padding:10px 30px;
            display:flex;align-items:center;justify-content:space-between;">

  <!-- ซ้าย -->
  <div style="display:flex;align-items:center;gap:8px;font-size:20px;font-weight:600;">
    <span class="dino">🦖</span>
    <span>Dinosaur Fai .com</span>
  </div>

  <!-- กลาง -->
  <div style="flex:1; display:flex; justify-content:center; gap:40px; font-size:16px;">
    <div style="text-align:center;">
      <div style="font-weight:600;">Date</div>
      <div id="dateLabel"></div>
    </div>

    <div style="text-align:center;">
      <div style="font-weight:600;">Time</div>
      <div id="timeLabel"></div>
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
        hours + ":" + minutes + ":" + seconds;
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
    df_display["date_dt"] = pd.to_datetime(df_display["Date"], dayfirst=True, errors="coerce")
    df_display = df_display.dropna(subset=["date_dt"])

    if df_display.empty:
        st.warning("ไม่พบข้อมูลวันที่ที่ใช้งานได้")
        return

    min_date = df_display["date_dt"].min().date()
    max_date = df_display["date_dt"].max().date()

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

    # เก็บ date_dt ไว้ใช้เลือกแถวล่าสุด แล้วค่อย drop ก่อนโชว์ตาราง
    df_filtered_sorted = df_filtered.sort_values("date_dt").copy()

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

    if all(c in df_filtered_sorted.columns for c in mq):
        tmp = df_filtered_sorted[mq].replace("", pd.NA).dropna(how="all")
        if not tmp.empty:
            r = tmp.iloc[-1]  # ✅ แถวล่าสุดของช่วง filter

            usable_income = parse_bath(r["O"])
            expenses = parse_bath(r["P"])
            balance = parse_bath(r["Q"])

            # ✅ Average Pay : Day = Balance / Balance Date
            avg_pay_day = (balance / day_left) if day_left > 0 else 0.0

            # ✅ Balance Use Pay : Day = Average + 172.04
            balance_use_pay_day = avg_pay_day + 172.04

            # ✅ 1 Day Forecast = Balance / (วันคงเหลือของพรุ่งนี้)
            tomorrow_left = day_left - 1
            one_day_forecast = (balance / tomorrow_left) if tomorrow_left > 0 else 0.0

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
        else:
            st.info("ไม่พบข้อมูลในคอลัมน์ M-Q สำหรับคำนวณ KPI")
    else:
        st.info("ยังไม่พบคอลัมน์ M-Q ในข้อมูล (ตรวจ data_loader ว่าดึงมาแล้ว)")

    st.write("")

    # ---------------- ตาราง ----------------
    df_table = df_filtered.drop(columns=["date_dt"], errors="ignore")
    st.subheader("Daily Price Trend")
    chart_box = st.container()
    with chart_box:
        render_price_trend_chart(df_filtered_sorted, date_col="Date", price_col="Price")

    st.subheader("Summary by List")

    summary_df = build_list_summary_table(df_filtered)

    if summary_df is not None:
        render_summary_table_with_sticky_footer(summary_df)
    else:
        st.info("ไม่มีข้อมูลสำหรับสรุป")


    st.subheader(f"ข้อมูลหลัง Filter (จำนวน {len(df_table)} แถว)")
    st.dataframe(df_table, use_container_width=True)
