import streamlit as st
import pandas as pd


def bpi_question(label: str, captions: list, index: int = None) -> int:
    return st.radio(
        label=label,
        options=range(11),
        horizontal=True,
        captions=captions,
        index=index
    )


captions_pain = ["No pain", "", "", "", "", "", "",
                 "", "", "", "Pain as bad as you can imagine"]
captions_relief = ["No relief", "", "", "", "", "", "",
                   "", "", "", "Complete relief"]
captions_interference = ["Does not interfere", "", "", "", "", "", "",
                         "", "", "", "Completely interferes"]

with st.form("daily_pain_form"):
    # Date input - by default, today's date
    min_date = pd.Timestamp('2024-01-01')
    today = pd.Timestamp.today()
    date = st.date_input('Select a date to log your pain',
                         today,
                         min_value=min_date,
                         max_value=today)

    st.divider()

    bpi1 = st.radio('Throughout our lives, most of us have had pain from time to time (such as minor headaches, sprains, and toothaches). Have you had pain other than these everyday kinds of pain today?',
                    options=['Yes', 'No'],
                    horizontal=True)

    # Needs logic to show/hide the rest of the form based on the answer to bpi1

    # bpi2 chart here!

    st.divider()

    bpi3 = bpi_question(
        "Please rate your pain by marking the box beside the number that best describes your pain at its worst in the last 24 hours",
        captions_pain
    )

    bpi4 = bpi_question(
        "Please rate your pain by marking the box beside the number that best describes your pain at its least in the last 24 hours",
        captions_pain
    )

    bpi5 = bpi_question(
        "Please rate your pain by marking the box beside the number that best describes your pain on the average",
        captions_pain
    )
    bpi6 = bpi_question(
        "6. Please rate your pain by marking the box beside the number that tells how much pain you have right now",
        captions_pain
    )

    st.divider()

# bpi7 is "What treatments or medications are you receiving for your pain?"

    bpi8 = st.radio("In the last 24 hours, how much relief have pain treatments or medications provided? Please mark the box below the percentage that most shows how much relief you have received",
                    options=[f"{x * 10} %" for x in range(11)],
                    horizontal=True,
                    captions=captions_relief,
                    index=None)

    st.divider()

    "Mark the box beside the number that describes how, during the past 24 hours, pain has interfered with your:"

    bpi9a = bpi_question("General activity", captions_interference)
    bpi9b = bpi_question("Mood", captions_interference)
    bpi9c = bpi_question("Walking ability", captions_interference)
    bpi9d = bpi_question("Normal work (includes both work outside the home and housework)",
                         captions_interference)
    bpi9e = bpi_question("Relations with other people", captions_interference)
    bpi9f = bpi_question("Sleep", captions_interference)
    bpi9g = bpi_question("Enjoyment of life", captions_interference)

    st.divider()

    # Submit button
    submitted = st.form_submit_button('Submit')
