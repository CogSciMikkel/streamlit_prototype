import streamlit as st
import pandas as pd
import os
import re


def display_create_entry():
    def get_pain_options():
        return [
            "✅ 0 - No pain",
            "🟢 1",
            "🟢 2",
            "🟡 3",
            "🟡 4",
            "🟠 5",
            "🟠 6",
            "🟠 7",
            "🔴 8",
            "🔴 9",
            "🚫 10 - Worst imaginable pain"
        ]

    def get_relief_options():
        return [
            "✅ 100 % - Complete relief",
            "🟢 90 %",
            "🟢 80 %",
            "🟡 70 %",
            "🟡 60 %",
            "🟠 50 %",
            "🟠 40 %",
            "🟠 30 %",
            "🔴 20 %",
            "🔴 10 %",
            "🚫 0 % - No relief"
        ]

    def get_interference_options():
        return [
            "✅ 0 - Has not interfered",
            "🟢 1",
            "🟢 2",
            "🟡 3",
            "🟡 4",
            "🟠 5",
            "🟠 6",
            "🟠 7",
            "🔴 8",
            "🔴 9",
            "🚫 10 - Has interfered completely"
        ]

    def bpi_question(label: str = "Question Placeholder", options: list = range(11), index: int = None) -> int:
        return st.selectbox(
            label=label,
            options=options,
            # horizontal=False,
            # captions=captions,
            index=index
        )

    def extract_number(value):
        if isinstance(value, str):
            match = re.search(r'\d+', value)
            if match:
                return int(match.group())
        return value

    def save_submission(data: dict, filename="pain_log.csv"):
        df = pd.DataFrame([data])  # one-row dataframe
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)

    # Title + Date
    st.title("🩺 Log your pain")
    today = pd.Timestamp.today()
    date = st.date_input("Date", today, max_value=today)

    st.divider()

    # bpi1: Have you had pain today?
    bpi1 = st.radio("Have you had any pain today other than minor everyday aches (like headaches or toothaches)?",
                    options=["No", "Yes"], horizontal=True)

    # Logic split based on answer
    if bpi1 == "No":
        # Auto-fill zeros and show success message
        if st.button("Submit no pain report"):
            data = {
                "date": date,
                "bpi1": bpi1,
                "bpi3": 0,
                "bpi4": 0,
                "bpi5": 0,
                "bpi6": 0,
                "bpi7": "",
                "bpi8": "0 %",
                "bpi9a": 0,
                "bpi9b": 0,
                "bpi9c": 0,
                "bpi9d": 0,
                "bpi9e": 0,
                "bpi9f": 0,
                "bpi9g": 0,
            }
            st.success("✅ Your no-pain report was submitted.")

    else:
        # Body map
        bpi2 = st.multiselect(
            "Please select the area(s) of your body that hurt(s) the most",
            options=["Head", "Neck", "Shoulder", "Arm", "Hand",
                     "Back", "Chest", "Abdomen", "Hip", "Leg", "Foot"]
        )

        # Pain ratings
        st.subheader("Please rate your pain in the past 24 hours")
        bpi3 = bpi_question(
            "Your pain at its worst", get_pain_options())
        bpi4 = bpi_question(
            "Your pain at its least", get_pain_options())
        bpi5 = bpi_question("Your pain on average", get_pain_options())
        bpi6 = bpi_question("Your pain right now", get_pain_options())

        st.divider()

        bpi7_intro = st.radio(
            "Are you using any treatments or meds for your pain?",
            options=['No', 'Yes'],
            horizontal=True
        )

        # Initialize bpi7 and bpi8 to avoid undefined variables error
        bpi7 = ""
        bpi8 = "0 %"

        if bpi7_intro == "Yes":
            bpi7 = st.text_input(
                "What pain treatments or meds are you using?",
                placeholder="e.g. paracetamol, physical therapy, meditation",
                max_chars=100
            )

            if bpi7:
                bpi8 = bpi_question(
                    "How much relief have your pain treatments/meds given in the past 24 hours?", get_relief_options())

        st.divider()

        st.subheader(
            "In the past 24 hours, how much has pain interfered with your...")

        bpi9a = bpi_question("general activity?", get_interference_options())
        bpi9b = bpi_question("mood?", get_interference_options())
        bpi9c = bpi_question("walking?", get_interference_options())
        bpi9d = bpi_question("normal work (incl. housework)?",
                             get_interference_options())
        bpi9e = bpi_question("relations with other people?",
                             get_interference_options())
        bpi9f = bpi_question("sleep?", get_interference_options())
        bpi9g = bpi_question("enjoyment of life?", get_interference_options())

        st.divider()

        if st.button("Submit"):
            data = {
                "date": date,
                "bpi1": bpi1,
                "bpi2": ", ".join(bpi2),
                "bpi3": extract_number(bpi3),
                "bpi4": extract_number(bpi4),
                "bpi5": extract_number(bpi5),
                "bpi6": extract_number(bpi6),
                "bpi7": bpi7,
                "bpi8": extract_number(bpi8),
                "bpi9a": extract_number(bpi9a),
                "bpi9b": extract_number(bpi9b),
                "bpi9c": extract_number(bpi9c),
                "bpi9d": extract_number(bpi9d),
                "bpi9e": extract_number(bpi9e),
                "bpi9f": extract_number(bpi9f),
                "bpi9g": extract_number(bpi9g),
            }
            save_submission(data)
            # Display the submitted data for confirmation
            st.success("✅ Your pain report was submitted.")
