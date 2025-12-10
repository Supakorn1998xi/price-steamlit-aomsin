# home_page.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def render_home(df):
    # ใช้เวลาปัจจุบันแค่สำหรับ Last Update (คำนวณครั้งเดียวตอนโหลด)
    last_update_str = datetime.now().strftime("%d %b %Y , %H:%M:%S")

    header_html = f"""
<div style="background-color:#1f1f1f;color:#ffffff;padding:10px 30px;
            display:flex;align-items:center;justify-content:space-between;">

  <!-- ซ้าย: โลโก้ + ชื่อ -->
  <div style="display:flex;align-items:center;gap:8px;
              font-size:20px;font-weight:600;">
    <span style="font-size:28px;">🦖</span>
    <span>Dinosaur Fai .com</span>
  </div>

  <!-- กลาง: Date + Time (JS อัปเดตเอง) -->
  <div style="text-align:center;flex:1;font-size:16px;">
    <div style="font-weight:600;">Date</div>
    <div>
      <span id="dateLabel"></span>
      &nbsp;&nbsp;&nbsp;
      <span id="timeLabel"></span>
    </div>
  </div>

  <!-- ขวา: Last Update (คงที่ตามตอนโหลดข้อมูล) -->
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
    var monthNames = ['Jan','Feb','Mar','Apr','May','Jun',
                      'Jul','Aug','Sep','Oct','Nov','Dec'];
    var month = monthNames[now.getMonth()];
    var year = now.getFullYear();
    var weekdayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    var weekday = weekdayNames[now.getDay()];

    var hours = pad(now.getHours());
    var minutes = pad(now.getMinutes());
    var seconds = pad(now.getSeconds());

    var dateText = day + ' ' + month + ' ' + year + ' (' + weekday + ')';
    var timeText = 'Time ' + hours + ':' + minutes + ':' + seconds;

    var dateEl = document.getElementById('dateLabel');
    var timeEl = document.getElementById('timeLabel');

    if (dateEl && timeEl) {{
      dateEl.textContent = dateText;
      timeEl.textContent = timeText;
    }}
  }}

  // อัปเดตทันที และทุก ๆ 1 วินาที
  updateClock();
  setInterval(updateClock, 1000);
</script>
"""

    # ใช้ components.html เพื่อให้ script ทำงานฝั่ง browser
    components.html(header_html, height=80)

    st.write("")
    st.dataframe(df, use_container_width=True)
