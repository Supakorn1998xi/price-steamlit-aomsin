# main.py
import streamlit as st
from data_loader import load_data
from home_page import render_home


def main():
    st.set_page_config(
        page_title="Price Dashboard",
        page_icon="📈",
        layout="wide",
    )

    try:
        df = load_data()
        render_home(df)
    except Exception as e:
        st.error(f"มีปัญหาในการดึงข้อมูล: {e}")


if __name__ == "__main__":
    main()
