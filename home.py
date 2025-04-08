import streamlit as st
import datetime
from log_data2 import display_log_form
from view_data import display_reports

#Page configuration
st.set_page_config(
    page_title = "Pain tracker",
    page_icon = ":pill:",
    layout = "wide",
    initial_sidebar_state="collapsed"
)

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
    # Should check against database
    if username and password:
        st.session_state.username = username
        st.session_state.logged_in = True
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


# Navigation
def display_login():

    col1, col2, col3 = st.columns([1, 2, 1]) # Centering login

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

def bottom_navigation():
    current_page = st.session_state.page
    
    home_active = "active" if current_page == "home" else ""
    create_active = "active" if current_page == "create_entry" else ""
    reports_active = "active" if current_page == "reports" else ""
    
    bottom_nav_html = f"""
    <div class="bottom-nav">
        <div class="nav-button {home_active}" onclick="window.location.href='/?home'">Home</div>
        <div class="nav-button {create_active}" onclick="window.location.href='/?create_entry'">Create Entry</div>
        <div class="nav-button {reports_active}" onclick="window.location.href='/?reports'">Reports</div>
    </div>
    """
    
    # Render the bottom navigation bar
    st.markdown(bottom_nav_html, unsafe_allow_html=True)

# Home page
def display_home():
    # Container for main content with padding for bottom nav
    with st.container():
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        # Whatever we want displayed 
        st.subheader("Something relevant")

        if st.button("Create Entry"):
            st.session_state.page = "create_entry"
            st.experimental_rerun() 

        st.markdown('</div>', unsafe_allow_html=True)

def display_profile():
    st.write("Profile page coming soon")

def main():
    # Load external CSS
    load_css("styles.css")
    
    query_params = st.query_params
    if "home" in query_params:
        st.session_state.page = "home"
    elif "create_entry" in query_params:
        st.session_state.page = "create_entry"
    elif "reports" in query_params:
        st.session_state.page = "reports"
    elif "profile" in query_params:
        st.session_state.page = "profile"
    
 # Display the appropriate page
    if not st.session_state.logged_in:
        display_login()
    else:
        
        greeting = get_greeting()
        st.subheader(f"{greeting}, {st.session_state.username}!")
        
        # Display the current page
        if st.session_state.page == "home":
            display_home()
        elif st.session_state.page == "create_entry":
            display_log_form()  # Call the function from log_data.py
        elif st.session_state.page == "reports":
            display_reports()
        elif st.session_state.page == "profile":
            display_profile()
    
    bottom_navigation()

# Run the app
if __name__ == "__main__":
    main()