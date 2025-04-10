import streamlit as st
import pandas as pd
import altair as alt
import os


def display_reports():
    st.title("📊 Pain Report Dashboard")

    csv_file = "pain_log.csv"

    # Load CSV
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"])

        # Sort by date (if not already)
        df = df.sort_values("date")

        st.subheader(
            "🗂 Logged Pain Data (I DON'T THINK THIS SHOULD BE AT THE TOP IN THE FINAL VERSION)")
        st.dataframe(df, use_container_width=True)

        st.divider()

        # Date filter
        if df['date'].dropna().empty:
            st.warning("No valid dates available in the data.")
        else:
            min_date = df['date'].min()
            max_date = df['date'].max()

            # Optional: set fallback default if needed
            if pd.isna(min_date) or pd.isna(max_date):
                min_date = pd.Timestamp("2022-01-01")
                max_date = pd.Timestamp("2022-12-31")

        date_range = st.sidebar.date_input(
            "Select date range", [min_date, max_date])

        # Filter based on selection
        if len(date_range) == 2:
            df_filtered = df[(df["date"] >= pd.to_datetime(date_range[0])) &
                             (df["date"] <= pd.to_datetime(date_range[1]))]
        else:
            df_filtered = df

        mean_bpi5 = df_filtered["bpi5"].mean()
        mean_bpi9a = df_filtered["bpi9a"].mean()
        mean_bpi9g = df_filtered["bpi9g"].mean()

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Pain", f"{mean_bpi5:.2f}")
        col2.metric("Average interference with general activity",
                    f"{mean_bpi9a: .2f}")
        col3.metric("Average interference with enjoyment of life",
                    f"{mean_bpi9g: .2f}")

        # Pain over time
        st.subheader("📈 Pain Over Time")

        # bpi3, bpi4, bpi5 over time
        # Prepare data for multi-line chart
        pain_cols = ["bpi3", "bpi4", "bpi5"]
        melted_df = df_filtered[["date"] + pain_cols].melt(
            id_vars="date", var_name="Pain Type", value_name="Score"
        )

        # Create Altair line chart
        line_chart = alt.Chart(melted_df).mark_line(point=True).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("Score:Q", title="Pain Score",
                    scale=alt.Scale(domain=[0, 10])),
            color=alt.Color("Pain Type:N", title="Pain Question"),
            tooltip=["date", "Pain Type", "Score"]
        ).properties(
            width=700,
            height=400,
            title="Pain Score Trends (bpi3, bpi4, bpi5)"
        )

        st.altair_chart(line_chart, use_container_width=True)

    else:
        st.warning(
            "⚠️ No data found. Please submit some entries in the main app first.")
