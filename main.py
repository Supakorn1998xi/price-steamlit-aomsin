# main.py
import streamlit as st
from data_loader import load_data
from home_page import render_home
import plotly.graph_objects as go

def main():
    st.set_page_config(
        page_title="Price Dashboard",
        page_icon="📈",
        layout="wide",
    )

    try:
        # 🔄 Spinner ตอนโหลดข้อมูลจริง (เห็นแน่นอน)
        with st.spinner("⏳ Loading data from Google Sheet..."):
            df = load_data()

        # 🔄 Spinner ตอนเตรียม Dashboard
        with st.spinner("⚙️ Preparing dashboard..."):
            render_home(df)

    except Exception as e:
        st.error("❌ มีปัญหาในการโหลดข้อมูล")
        st.exception(e)


if __name__ == "__main__":
    main()
