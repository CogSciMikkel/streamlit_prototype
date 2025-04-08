import streamlit as st
import pandas as pd
import os

def display_log_form():
    
    def bpi_question(label: str, captions: list, index: int = None) -> int:
        return st.radio(
            label=label,
            options=range(11),
            horizontal=False,
            captions=captions,
            index=index
        )


    def save_submission(data: dict, filename="pain_log.csv"):
        df = pd.DataFrame([data])  # one-row dataframe
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)


    captions_pain = ["No pain", "", "", "", "", "", "",
                    "", "", "", "Pain as bad as you can imagine"]
    captions_relief = ["No relief", "", "", "", "", "", "",
                    "", "", "", "Complete relief"]
    captions_interference = ["Does not interfere", "", "", "", "", "", "",
                            "", "", "", "Completely interferes"]

    # Title + Date
    st.title("🩺 Log your pain")
    today = pd.Timestamp.today()
    date = st.date_input("Date", today, max_value=today)

    st.divider()

    # bpi1: Have you had pain today?
    bpi1 = st.radio("Have you had any pain today (other than everyday types like minor headaches, sprains, and toothaches)?",
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
        # Show full form dynamically
        st.subheader("Please answer the following about your pain today:")

        # Body map
        bpi2 = st.multiselect(
            "Please select the areas of your body that hurts the most",
            options=["Head", "Neck", "Shoulder", "Back",
                    "Chest", "Abdomen", "Hip", "Leg", "Arm"]
        )

        # Pain ratings
        st.subheader("Please rate your pain in the past 24 hours")
        bpi3 = bpi_question(
            "Your pain at its worst", captions_pain)
        bpi4 = bpi_question(
            "Your pain at its least", captions_pain)
        bpi5 = bpi_question("Your pain on average", captions_pain)
        bpi6 = bpi_question("Your pain right now", captions_pain)

        st.divider()

        bpi7_intro = st.radio(
            "Are you receiving any treatments or medications for your pain?",
            options=['No', 'Yes'],
            horizontal=True
        )

        # Initialize bpi7 and bpi8 to avoid undefined variables error
        bpi7 = ""
        bpi8 = "0 %"

        if bpi7_intro == "Yes":
            bpi7 = st.text_input(
                "What treatments or medications are you receiving?",
                placeholder="e.g. Paracetamol, physical therapy, meditation",
                max_chars=100
            )
            if bpi7:
                bpi8 = st.radio("How much relief have treatments provided (past 24h)?",
                                options=[f"{x * 10} %" for x in range(11)],
                                horizontal=True,
                                captions=captions_relief)

        st.divider()
        st.write("Pain interference with activities (past 24h):")

        bpi9a = bpi_question("General activity", captions_interference)
        bpi9b = bpi_question("Mood", captions_interference)
        bpi9c = bpi_question("Walking ability", captions_interference)
        bpi9d = bpi_question("Normal work", captions_interference)
        bpi9e = bpi_question("Relations with other people", captions_interference)
        bpi9f = bpi_question("Sleep", captions_interference)
        bpi9g = bpi_question("Enjoyment of life", captions_interference)

        st.divider()

        if st.button("Submit"):
            data = {
                "date": date,
                "bpi1": bpi1,
                "bpi3": bpi3,
                "bpi4": bpi4,
                "bpi5": bpi5,
                "bpi6": bpi6,
                "bpi7": bpi7,
                "bpi8": bpi8,
                "bpi9a": bpi9a,
                "bpi9b": bpi9b,
                "bpi9c": bpi9c,
                "bpi9d": bpi9d,
                "bpi9e": bpi9e,
                "bpi9f": bpi9f,
                "bpi9g": bpi9g,
            }
            save_submission(data)
            # Display the submitted data for confirmation
            st.success("✅ Your pain report was submitted.")
