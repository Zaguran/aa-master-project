import streamlit as st
from components import auth, session

st.set_page_config(page_title="Login / Logout", page_icon="🔐", layout="centered")

session.init_session_state()

if auth.is_authenticated():
    user = auth.get_current_user()

    st.success(f"Already logged in as: {user['full_name']} ({user['email']})")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Go to App", type="primary", use_container_width=True):
            st.switch_page("app.py")

    with col2:
        if st.button("Logout", type="secondary", use_container_width=True):
            auth.logout()
            st.success("Logged out successfully!")
            st.rerun()

    st.stop()

st.title("🔐 Login / Logout")
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
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

st.markdown("---")
st.markdown("**Default credentials:** admin@aat.local / VeryStrongAdminPwd")
