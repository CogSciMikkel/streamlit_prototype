import streamlit as st

# Needs actual user authentication
# For now, just a simple login/logout button

# Navigation
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login/logout functions


def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


# Pages
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

log_data = st.Page("log_data.py", title="Log your pain",
                   icon=":material/insert_chart_outlined:")

log_data2 = st.Page("log_data2.py", title="Log your pain (2nd test)",
                    icon=":material/insert_chart_outlined:")


view_data = st.Page("view_data.py", title="View your pain data",
                    icon=":material/visibility:")

# Navigation
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Your Pain": [log_data, log_data2, view_data],
            "Account": [logout_page],

        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
