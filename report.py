import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
import altair as alt
import os


def display_reports():
    st.title("📊 Pain Report Dashboard")

    # Load CSV
    csv_file = "pain_log.csv"

    # Guard clause against missing file
    if not os.path.exists(csv_file):
        st.warning(
            "⚠️ No data found. Please create an entry first.")
        return

    # Read CSV with date parsing
    df = pd.read_csv(csv_file, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce')

    # Sort by date (if not already)
    df = df.sort_values("date")

    # Data frame for display - should be removed in the final version
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

    # --- Display metrics ---
    # Average pain this week vs last week
    # Define current and previous week ranges
    today = pd.Timestamp.today().normalize()
    start_of_this_week = today - pd.Timedelta(days=today.weekday())  # Monday
    start_of_last_week = start_of_this_week - pd.Timedelta(weeks=1)
    end_of_last_week = start_of_this_week - pd.Timedelta(days=1)

    # Filter data for each week
    this_week_df = df_filtered[(df_filtered["date"] >= start_of_this_week) & (
        df_filtered["date"] <= today)]
    last_week_df = df_filtered[(df_filtered["date"] >= start_of_last_week) & (
        df_filtered["date"] <= end_of_last_week)]

    # Compute average bpi5
    mean_this_week = this_week_df["bpi5"].mean()
    mean_last_week = last_week_df["bpi5"].mean()

    # Compute delta (change from last week)
    if pd.notna(mean_this_week) and pd.notna(mean_last_week):
        delta = mean_this_week - mean_last_week
    else:
        delta = None  # Show no delta if data is missing

    # Most painful area this week compared to last week
    # Get the most painful area for this week and last week based on strings in bpi2
    this_week_areas = this_week_df["bpi2"].dropna(
    ).str.split(",").explode().str.strip()
    last_week_areas = last_week_df["bpi2"].dropna(
    ).str.split(",").explode().str.strip()

    # Display two metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Average Pain (This Week)",
            value=f"{mean_this_week:.2f}" if pd.notna(
                mean_this_week) else "No data",
            delta=f"{delta:+.2f}" if delta is not None else "N/A",
            delta_color="inverse",
            border=True
        )
    with col2:
        # Most painful area this week compared to last week
        st.metric(
            label="Most Painful Area (This Week)",
            value=this_week_areas.value_counts().idxmax(
            ) if not this_week_areas.empty else "No data",
            delta="N/A",  # Placeholder for now
            delta_color="off",
            border=True
        )

    # --- Display pain over time ---
    st.subheader("📈 Pain Over Time")

    # bpi3, bpi4, bpi5 over time
    # Prepare data for multi-line chart
    pain_col_labels = {
        "bpi3": "Worst",
        "bpi4": "Least",
        "bpi5": "Average",
        "bpi6": "Right Now"
    }

    pain_cols = list(pain_col_labels.keys())

    range_option = st.radio(
        "Select time range:",
        ["Last 7 days", "Last month", "Last year", "All time"],
        horizontal=True
    )

    # Calculate date cutoff based on selection
    today = pd.Timestamp.today().normalize()

    if range_option == "Last 7 days":
        cutoff = today - pd.Timedelta(days=7)
    elif range_option == "Last month":
        cutoff = today - pd.DateOffset(months=1)
    elif range_option == "Last year":
        cutoff = today - pd.DateOffset(years=1)
    else:
        cutoff = None  # "All time"

    # Filter df_filtered accordingly
    if cutoff is not None:
        df_chart = df_filtered[df_filtered["date"] >= cutoff]
    else:
        df_chart = df_filtered

    # Melt the DataFrame for Altair - this is necessary for Altair to plot multiple lines
    melted_df = df_chart[["date"] + pain_cols].melt(
        id_vars="date", var_name="Pain Type", value_name="Score"
    )
    melted_df["Pain Type"] = melted_df["Pain Type"].map(
        pain_col_labels)

    # Create Altair line chart
    line_chart = alt.Chart(melted_df).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("Score:Q", title="Score",
                scale=alt.Scale(domain=[0, 10])),
        color=alt.Color("Pain Type:N", title="Pain"),
        tooltip=["date", "Pain Type", "Score"]
    ).properties(
        width=700,
        height=400,
        title=""
    )

    # Display the chart
    st.altair_chart(line_chart, use_container_width=True)

    # --- Display pain interference radar plot ---
    st.subheader("Your Average Pain Interference")

    interference_vars = ["bpi9a", "bpi9b", "bpi9c",
                         "bpi9d", "bpi9e", "bpi9f", "bpi9g"]

    # Create readable labels
    labels = {
        "bpi9a": "General Activity",
        "bpi9b": "Mood",
        "bpi9c": "Walking Ability",
        "bpi9d": "Normal Work",
        "bpi9e": "Relations",
        "bpi9f": "Sleep",
        "bpi9g": "Enjoyment of Life"
    }

    # Compute mean values
    mean_scores = df_filtered[interference_vars].mean()

    # Prepare data for radar plot
    radar_df = pd.DataFrame({
        "Factor": [labels[var] for var in interference_vars],
        "Score": [mean_scores[var] for var in interference_vars]
    })

    # Create radar plot with Plotly
    fig = px.line_polar(radar_df, r="Score",
                        theta="Factor", line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
        title="BPI Interference Radar Chart",
        polar=dict(
            radialaxis=dict(range=[0, 10], visible=True)
        ),
        showlegend=True
    )

    # Display the radar plot in a central column to avoid labels falling off
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=True)
