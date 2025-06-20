# utils/auth.py

import streamlit as st

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "admin123",
    "guest": "guestpass"
}

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""

    if not st.session_state.authenticated:
        with st.form("login"):
            st.subheader("🔐 Login Required")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit and USER_CREDENTIALS.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! ✅")
                st.rerun()
            elif submit:
                st.error("Invalid credentials")
        st.stop()
