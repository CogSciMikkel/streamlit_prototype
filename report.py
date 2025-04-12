import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import os


def display_reports():
    st.title("Your Pain Report")

    # Load CSV
    csv_file = "pain_log.csv"

    # Guard clause against missing file
    if not os.path.exists(csv_file):
        st.warning(
            "⚠️ No data found. Please create an entry first.")
        return

    # Read CSV with date parsing
    df = pd.read_csv(csv_file, sep=";", parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce')

    # Sort by date (if not already)
    df = df.sort_values("date")

    # Data frame for display - should be removed in the final version
    # st.subheader(
    #     "🗂 Logged Pain Data (I DON'T THINK THIS SHOULD BE AT THE TOP IN THE FINAL VERSION)")
    # st.dataframe(df, use_container_width=True)

    # Choose time range
    range_option = st.radio(
        "**Select time range**",
        ["Last 7 days", "Last month", "Last year", "All time"],
        horizontal=True
    )

    # Choose period
    if range_option == "Last 7 days":
        period = "Weekly"
    elif range_option == "Last month":
        period = "Monthly"
    elif range_option == "Last year":
        period = "Yearly"
    else:
        period = "All Time"

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

    df_filtered = df.copy()

    st.divider()

    # --- Display metrics ---
    st.subheader(f"📊 {period} Comparison")

    # Average pain this week vs last week
    # Define current and previous week ranges
    today = pd.Timestamp.today().normalize()
    if range_option == "Last 7 days":
        this_start = today - pd.Timedelta(days=6)
        last_start = this_start - pd.Timedelta(days=7)
        last_end = this_start - pd.Timedelta(days=1)
    elif range_option == "Last month":
        this_start = today - pd.DateOffset(days=30)
        last_start = this_start - pd.DateOffset(days=30)
        last_end = this_start - pd.Timedelta(days=1)
    elif range_option == "Last year":
        this_start = today - pd.DateOffset(years=1)
        last_start = this_start - pd.DateOffset(years=1)
        last_end = this_start - pd.Timedelta(days=1)
    else:  # All time
        this_start = df["date"].min()
        last_start = None  # skip comparison
        last_end = None

    # Filter data for each week
    this_period_df = df[(df["date"] >= this_start) & (df["date"] <= today)]

    if last_start is not None and last_end is not None:
        last_period_df = df[(df["date"] >= last_start)
                            & (df["date"] <= last_end)]
    else:
        last_period_df = pd.DataFrame(columns=df.columns)

    # Compute average bpi5
    mean_this_period = this_period_df["bpi5"].mean()
    mean_last_period = last_period_df["bpi5"].mean()

    # Compute delta (change from last week)
    if pd.notna(mean_this_period) and pd.notna(mean_last_period):
        delta = mean_this_period - mean_last_period
    else:
        delta = None

    # Most painful area this week compared to last week
    # Get the most painful area for this week and last week based on strings in bpi2
    from collections import Counter

    def get_most_common_word(series):
        # Flatten list of strings -> individual words
        all_words = []
        for entry in series.dropna():
            if isinstance(entry, str):
                words = [word.strip() for word in entry.split(',')
                         ]  # or .split() if space-separated
                all_words.extend(words)
        return Counter(all_words).most_common(1)[0][0] if all_words else None

    # Process bpi2 text entries
    this_areas = this_period_df["bpi2"]
    last_areas = last_period_df["bpi2"]

    most_common_this = get_most_common_word(this_areas)
    most_common_last = get_most_common_word(last_areas)

    if most_common_this and most_common_last:
        area_delta = f"was {most_common_last}" if most_common_this != most_common_last else "No change"
    else:
        area_delta = "N/A"

    # Display two metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=f"Average Pain Score ({range_option})",
            value=f"{mean_this_period:.2f}" if pd.notna(
                mean_this_period) else "No data",
            delta=f"{delta:+.2f}" if delta is not None else "N/A",
            delta_color="inverse",
            border=True
        )
    with col2:
        st.metric(
            label=f"Most Painful Area ({range_option})",
            value=most_common_this if most_common_this else "No data",
            delta=area_delta,
            delta_color="off",
            border=True
        )

        st.divider()

    # --- Display pain over time ---
    st.subheader(f"📈 {period} Trends")

    # Define pain variables to plot (excluding bpi6)
    pain_col_labels = {
        "bpi3": "Worst",
        "bpi4": "Least",
        "bpi5": "Average"
    }
    pain_cols = list(pain_col_labels.keys())

    today = pd.Timestamp.today().normalize()

    if range_option == "Last 7 days":
        cutoff = today - pd.Timedelta(days=7)
    elif range_option == "Last month":
        cutoff = today - pd.DateOffset(months=1)
    elif range_option == "Last year":
        cutoff = today - pd.DateOffset(years=1)
    else:
        cutoff = None  # All time

    df_chart = df_filtered[df_filtered["date"] >=
                           cutoff] if cutoff is not None else df_filtered.copy()

    if range_option == "Last 7 days":
        df_chart["period"] = df_chart["date"]
        agg_df = df_chart[["period"] + pain_cols].copy()
    elif range_option == "Last month":
        df_chart["period"] = df_chart["date"].dt.to_period(
            "W").apply(lambda r: r.start_time)
        agg_df = df_chart.groupby("period")[pain_cols].mean().reset_index()
    else:  # Last year or All time
        df_chart["period"] = df_chart["date"].dt.to_period(
            "M").apply(lambda r: r.start_time)
        agg_df = df_chart.groupby("period")[pain_cols].mean().reset_index()

    # Melt after aggregation
    melted_df = agg_df.melt(
        id_vars="period", var_name="Pain Code", value_name="Score")
    melted_df["Pain Type"] = melted_df["Pain Code"].map(pain_col_labels)

    # Drop rows with missing values
    melted_df = melted_df.dropna(subset=["Score", "Pain Type"])

    # Define color and dash styles
    color_scale = alt.Scale(domain=["Worst", "Least", "Average"],
                            range=["red", "green", "#1f77b4"])
    dash_scale = alt.Scale(domain=["Worst", "Least", "Average"],
                           range=[[4, 4], [4, 4], [0]])

    # Create Altair chart
    line_chart = alt.Chart(melted_df).mark_line(point=(range_option == "Last 7 days")).encode(
        x=alt.X("period:T", title="Date"),
        y=alt.Y("Score:Q", title="Score", scale=alt.Scale(domain=[0, 10])),
        color=alt.Color("Pain Type:N", title="Pain Type", scale=color_scale),
        strokeDash=alt.StrokeDash("Pain Type:N", scale=dash_scale),
        opacity=alt.condition(
            alt.FieldOneOfPredicate(
                field="Pain Type", oneOf=["Worst", "Least"]),
            alt.value(0.8),
            alt.value(1.0)
        ),
        tooltip=[
            alt.Tooltip("period:T", title="Date"),
            alt.Tooltip("Pain Type:N"),
            alt.Tooltip("Score:Q", title="Score", format=".2f")
        ]
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(line_chart, use_container_width=True)

    st.divider()

    # --- Display pain interference bar plot ---
    st.subheader(f"{period} Pain Interference")

    interference_vars = ["bpi9a", "bpi9b", "bpi9c",
                         "bpi9d", "bpi9e", "bpi9f", "bpi9g"]

    labels = {
        "bpi9a": "General Activity",
        "bpi9b": "Mood",
        "bpi9c": "Walking",
        "bpi9d": "Normal Work",
        "bpi9e": "Relations",
        "bpi9f": "Sleep",
        "bpi9g": "Enjoyment of Life"
    }

    # Apply the same range_option filter
    today = pd.Timestamp.today().normalize()
    if range_option == "Last 7 days":
        cutoff = today - pd.Timedelta(days=7)
    elif range_option == "Last month":
        cutoff = today - pd.DateOffset(months=1)
    elif range_option == "Last year":
        cutoff = today - pd.DateOffset(years=1)
    else:
        cutoff = None

    df_interference = df_filtered[df_filtered["date"]
                                  >= cutoff] if cutoff is not None else df_filtered

    # Compute mean interference scores
    mean_scores = df_interference[interference_vars].mean()

    # Build a DataFrame with friendly names and corresponding mean scores
    interference_df = pd.DataFrame({
        "Factor": [labels[var] for var in interference_vars],
        "Score": [mean_scores[var] for var in interference_vars]
    })

    # Create a horizontal bar chart
    interference_bar_chart = alt.Chart(interference_df).mark_bar().encode(
        y=alt.Y("Factor:N", title=""),
        x=alt.X("Score:Q", title="Average Score",
                scale=alt.Scale(domain=[0, 10])),
        tooltip=[
            alt.Tooltip("Factor:N", title="Interference with"),
            alt.Tooltip("Score:Q", title="Average Score", format=".2f")
        ]
    ).properties(
        width=700,
        height=400
    )

    # Add text labels showing the score on each bar
    interference_text = interference_bar_chart.mark_text(
        align="left",
        baseline="middle",
        dx=3,  # Nudges text to the right
        color="white"
    ).encode(
        text=alt.Text("Score:Q", format=".2f")
    )

    # Layer the text on top of the bars
    interference_chart = interference_bar_chart + interference_text

    st.altair_chart(interference_chart, use_container_width=True)

    st.divider()

    # --- Display Treatment Comparisons ---
    st.subheader(f"💊 {period} Treatment Comparisons")

    # Filter the DataFrame based on the cutoff (if provided)
    df_bpi7 = df_filtered[df_filtered["date"] >=
                          cutoff] if cutoff is not None else df_filtered.copy()

    # Replace missing bpi7 values with a label "None"
    df_bpi7["bpi7_clean"] = df_bpi7["bpi7"].fillna("None")

    # Group by bpi7_clean and compute the mean bpi5
    bpi7_mean = df_bpi7.groupby("bpi7_clean", dropna=False)[
        "bpi5"].mean().reset_index()
    bpi7_mean = bpi7_mean.rename(columns={"bpi5": "mean_bpi5"})

    # Create Altair bar plot
    bar_chart = alt.Chart(bpi7_mean).mark_bar().encode(
        y=alt.Y("bpi7_clean:N", title=""),
        x=alt.X("mean_bpi5:Q", title="Average Pain Score",
                scale=alt.Scale(domain=[0, 10])),
        tooltip=[
            alt.Tooltip("bpi7_clean:N", title="Treatment"),
            alt.Tooltip("mean_bpi5:Q",
                        title="Average Pain Score", format=".2f")
        ]
    ).properties(
        width=700,
        height=400
    )

    text_for_bar_chart = bar_chart.mark_text(
        align='left',
        baseline='middle',
        dx=3,  # Nudges text to right so it doesn't appear on top of the bar,
        color="white"
    ).encode(
        text=alt.Text("mean_bpi5:Q", format=".2f")
    )

    treatment_chart = (bar_chart + text_for_bar_chart)

    st.altair_chart(treatment_chart, use_container_width=True)

    treatment_expander = st.expander("How to interpret treatment comparisons")
    treatment_expander.write("""
        This chart shows the average pain on days you used a treatment. It does *not* mean that the treatment causes more or less pain.
        
        For example, if you only take painkillers when your pain is high, the chart may show high pain on those days. This just means that you take painkillers only on bad days, not that they cause more pain.
    """)

    # Radar plot (commented out for now, not intuitive)
    # fig = px.line_polar(
    #     radar_df,
    #     r="Score",
    #     theta="Factor",
    #     line_close=True
    # )
    # fig.update_traces(fill='toself')
    # fig.update_layout(
    #     polar=dict(radialaxis=dict(range=[0, 10], visible=True)),
    #     showlegend=False,
    #     title=f"Pain Interference Averages ({range_option})"
    # )

    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     st.plotly_chart(fig, use_container_width=True)
