import streamlit as st
from components import auth, session

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

session.init_session_state()

if auth.is_authenticated():
    st.success("You are already logged in!")
    st.info("Use the navigation menu to access different modules.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/01_Dashboard.py")
    st.stop()

st.title("🔐 AAT Login")
st.markdown("---")

with st.form("login_form"):
    email = st.text_input(
        "Email",
        placeholder="admin@aat.local",
        help="Enter your email address"
    )
    
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        help="Enter your password"
    )
    
    submit = st.form_submit_button("Login", use_container_width=True, type="primary")
    
    if submit:
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            with st.spinner("Authenticating..."):
                if auth.login(email, password):
                    st.success("Login successful! Redirecting...")
                    st.switch_page("pages/01_Dashboard.py")
                else:
                    st.error("Invalid email or password. Please try again.")

st.markdown("---")
st.markdown("**Default credentials:** admin@aat.local / admin123")
