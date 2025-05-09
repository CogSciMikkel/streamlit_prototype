from create_entry import display_create_entry
from report import display_reports
import datetime
import streamlit as st
import platform

# Page configuration
st.set_page_config(
    page_title="Pain tracker",
    page_icon=":pill:",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# To fix the issue with the day number formatting on Windows

def get_day_num(day):
    if platform.system() == "Windows":
        return day.strftime("%#d")
    else:
        return day.strftime("%-d")


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Initialize session start
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.datetime.now()

# Navigation functions


def go_to_page(page):
    st.session_state.page = page
    st.rerun()


# Login/logout functions
def authenticate(username, password):
    # Simple authentication for prototype
    if username and password:
        st.session_state.username = username
        st.session_state.logged_in = True
        
        # Check if there was a page parameter before login
        if "page" in st.query_params:
            page = st.query_params["page"]
            if page in ["home", "create_entry", "reports", "profile"]:
                st.session_state.page = page
        else:
            st.session_state.page = "home"
            
        st.rerun()
    else:
        st.error("Please enter both username and password")


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "login"
    st.rerun()


def get_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


def display_calendar():
    today = datetime.date.today()
    selected_date = st.session_state.get("selected_date", today)
    offset = st.session_state.get("calendar_offset", 0)
    base_date = today + datetime.timedelta(days=offset)

    days = [base_date + datetime.timedelta(days=i - 2) for i in range(7)]

    calendar_html = "<div class='scrollable-calendar'>"

    for i, day in enumerate(days):
        day_str = day.strftime("%a %d")
        is_today = day == today
        is_selected = day == selected_date

        classes = "calendar-day"
        if is_today:
            classes += " today"
        if is_selected:
            classes += " selected"

        # Add a query param to track the click
        calendar_html += (
            f"<form action='?day={day.isoformat()}' method='post' style='display:inline;'>"
            f"<button class='{classes}' type='submit'>{day_str}</button>"
            "</form>"
        )

    calendar_html += "</div>"
    st.markdown(calendar_html, unsafe_allow_html=True)

    # Use st.query_params instead of experimental API
    if "day" in st.query_params:
        try:
            new_day = datetime.date.fromisoformat(st.query_params["day"])
            st.session_state.selected_date = new_day
            st.query_params.clear()  # clear the param to avoid repeated reruns
            st.rerun()
        except Exception:
            pass

    st.markdown(
        f"<div style='text-align:center; margin-top:10px;'>"
        f"<b>{selected_date.strftime('%A, %d %B %Y')}</b></div>",
        unsafe_allow_html=True
    )

# Navigation


def display_login():

    col1, col2, col3 = st.columns([1, 2, 1])  # Centering login

    with col2:
        st.title("Pain Tracker")
        st.subheader("Please login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            authenticate(username, password)
    with col2:
        if st.button("Create Account", use_container_width=True):
            st.info("Account creation would be implemented here")

# Bottom navigation bar
def bottom_navigation():
    # Add a special class to this container via markdown
    st.markdown('<div class="nav-container"></div>', unsafe_allow_html=True)
    
    # Create three columns for the buttons within the container
    cols = st.columns(3)
    
    # Current page for highlighting active button
    current_page = st.session_state.page
    
    with cols[0]:
        if st.button("🏠", key="home_btn", 
                   use_container_width=True,
                   type="primary" if current_page == "home" else "secondary"):
            st.session_state.page = "home"
            st.rerun()
            
    with cols[1]:
        if st.button("➕", key="create_btn", 
                   use_container_width=True,
                   type="primary" if current_page == "create_entry" else "secondary"):
            st.session_state.page = "create_entry"
            st.rerun()
            
    with cols[2]:
        if st.button("📊", key="reports_btn", 
                   use_container_width=True,
                   type="primary" if current_page == "reports" else "secondary"):
            st.session_state.page = "reports"
            st.rerun()

# Home page
def display_home():
    col1, col2, col3 = st.columns([1, 2, 1])  # This will center the content

    with col2:
        greeting = get_greeting()
        st.markdown(
            f"<h3>{greeting}, {st.session_state.username}!</h3>", unsafe_allow_html=True)

        display_calendar()

        st.markdown(f"<h3>Something relevant</h3>", unsafe_allow_html=True)


def display_profile():
    st.write("Profile page coming soon")

def main():
    load_css("styles.css")

    # Initialize session state variables if they don't exist
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Check login status
    if not st.session_state.logged_in:
        display_login()
    else:
        # Display the current page based on session state
        if st.session_state.page == "home":
            display_home()
        elif st.session_state.page == "create_entry":
            display_create_entry()
        elif st.session_state.page == "reports":
            display_reports()
        elif st.session_state.page == "profile":
            display_profile()
        
        # Add navigation bar at the bottom for logged-in users
        bottom_navigation()

# Run the app
if __name__ == "__main__":
    main()
