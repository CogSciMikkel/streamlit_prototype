import streamlit as st
import pandas as pd
import altair as alt
import os

def display_reports():
    
    st.set_page_config(page_title="Pain Report", layout="wide")
    st.title("📊 Pain Report Dashboard")

    csv_file = "pain_log.csv"

    # Load CSV
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, parse_dates=["date"])

        # Sort by date (if not already)
        df = df.sort_values("date")

        st.subheader("🗂 Logged Pain Data")
        st.dataframe(df, use_container_width=True)

        st.divider()

        # Date filter
        st.sidebar.header("🔍 Filters")
        min_date = df["date"].min()
        max_date = df["date"].max()

        date_range = st.sidebar.date_input(
            "Select date range", [min_date, max_date])

        # Filter based on selection
        if len(date_range) == 2:
            df_filtered = df[(df["date"] >= pd.to_datetime(date_range[0])) &
                            (df["date"] <= pd.to_datetime(date_range[1]))]
        else:
            df_filtered = df

        st.subheader("📈 Pain Over Time")
        pain_metrics = ["bpi3", "bpi4", "bpi5", "bpi6"]

        for metric in pain_metrics:
            line = alt.Chart(df_filtered).mark_line(point=True).encode(
                x='date:T',
                y=alt.Y(f"{metric}:Q", scale=alt.Scale(domain=[0, 10])),
                tooltip=["date", metric]
            ).properties(
                title=f"{metric.upper()} (0 = no pain, 10 = worst imaginable)"
            )
            st.altair_chart(line, use_container_width=True)

        st.divider()

        st.subheader("🧭 Interference Factors")
        interference_factors = [
            col for col in df.columns if col.startswith("bpi9")]
        selected = st.multiselect("Choose factors to compare:",
                                interference_factors, default=interference_factors)

        if selected:
            chart_data = df_filtered[[
                "date"] + selected].melt("date", var_name="Factor", value_name="Score")
            bar = alt.Chart(chart_data).mark_line(point=True).encode(
                x="date:T",
                y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 10])),
                color="Factor:N",
                tooltip=["date", "Factor", "Score"]
            ).properties(
                title="Interference Scores Over Time"
            )
            st.altair_chart(bar, use_container_width=True)

        st.divider()

        st.subheader("📝 Summary Stats")
        st.dataframe(df_filtered.describe(
            numeric_only=True), use_container_width=True)

    else:
        st.warning(
            "⚠️ No data found. Please submit some entries in the main app first.")
