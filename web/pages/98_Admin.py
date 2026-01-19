import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")

from components import auth, session, layout, security
from agents.db_bridge import database

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

session.init_session_state()
user = auth.get_current_user()

if not auth.is_authenticated():
    st.warning("Please login to access the application.")
    if st.button("Goto Login Page", type="primary"):
        st.switch_page("pages/99_Login_Logout.py")
    st.stop()

auth.require_role(["admin"])

layout.render_header("Admin Panel")
st.title("⚙️ Admin Panel")

st.success(f"Welcome, {user['full_name']} (admin)")

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 User Management",
    "🏢 Customer Management",
    "🖥️ Platform Management",
    "⚙️ System Settings"
])

# ============================================================================
# TAB 1: USER MANAGEMENT
# ============================================================================
with tab1:
    st.subheader("User Management")

    # List all users
    try:
        users = database.list_all_users()
        if users:
            # Convert to DataFrame for display
            df = pd.DataFrame(users)
            # Format roles column
            if 'roles' in df.columns:
                df['roles'] = df['roles'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
            # Format boolean
            if 'is_active' in df.columns:
                df['is_active'] = df['is_active'].apply(lambda x: 'Yes' if x else 'No')
            # Select columns to display
            display_cols = ['email', 'full_name', 'roles', 'is_active', 'created_at']
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("No users found.")
    except Exception as e:
        st.error(f"Error loading users: {e}")

    st.markdown("---")

    # Create new user
    with st.expander("➕ Create New User"):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email*")
                password = st.text_input("Password*", type="password")
            with col2:
                full_name = st.text_input("Full Name*")
                password_confirm = st.text_input("Confirm Password*", type="password")

            initial_role = st.selectbox("Initial Role", ["visitor", "admin"])

            if st.form_submit_button("Create User", type="primary"):
                if not email or not full_name or not password:
                    st.error("All fields marked with * are required")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                elif '@' not in email:
                    st.error("Invalid email address")
                else:
                    password_hash = security.hash_password(password)
                    result = database.create_user(email, full_name, password_hash, initial_role)
                    if result.get("status") == "success":
                        st.success(f"User {email} created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create user: {result.get('message')}")

    # Manage user roles
    with st.expander("🔐 Manage User Roles"):
        try:
            users = database.list_all_users()
            if users:
                user_options = {f"{u['email']} ({u['full_name']})": str(u['user_id']) for u in users}
                selected_user = st.selectbox("Select User", list(user_options.keys()), key="role_user_select")

                if selected_user:
                    selected_user_id = user_options[selected_user]
                    selected_user_data = next((u for u in users if str(u['user_id']) == selected_user_id), None)

                    if selected_user_data:
                        current_roles = selected_user_data.get('roles', [])
                        st.write(f"**Current roles:** {', '.join(current_roles) if current_roles else 'None'}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Add Admin Role", key="add_admin"):
                                if database.assign_role_to_user(selected_user_id, 'admin'):
                                    st.success("Admin role added!")
                                    st.rerun()
                                else:
                                    st.error("Failed to add role")

                            if st.button("Add Visitor Role", key="add_visitor"):
                                if database.assign_role_to_user(selected_user_id, 'visitor'):
                                    st.success("Visitor role added!")
                                    st.rerun()
                                else:
                                    st.error("Failed to add role")

                        with col2:
                            if st.button("Remove Admin Role", key="remove_admin"):
                                if database.remove_role_from_user(selected_user_id, 'admin'):
                                    st.success("Admin role removed!")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove role")

                            if st.button("Remove Visitor Role", key="remove_visitor"):
                                if database.remove_role_from_user(selected_user_id, 'visitor'):
                                    st.success("Visitor role removed!")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove role")
            else:
                st.info("No users available")
        except Exception as e:
            st.error(f"Error: {e}")

    # Activate/Deactivate user
    with st.expander("🔄 Activate/Deactivate User"):
        try:
            users = database.list_all_users()
            if users:
                user_options = {f"{u['email']} - {'Active' if u['is_active'] else 'Inactive'}": (str(u['user_id']), u['is_active']) for u in users}
                selected_user = st.selectbox("Select User", list(user_options.keys()), key="status_user_select")

                if selected_user:
                    user_id, is_active = user_options[selected_user]

                    col1, col2 = st.columns(2)
                    with col1:
                        if is_active:
                            if st.button("❌ Deactivate User", type="secondary"):
                                if database.deactivate_user(user_id):
                                    st.success("User deactivated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to deactivate user")
                        else:
                            st.info("User is already inactive")

                    with col2:
                        if not is_active:
                            if st.button("✅ Activate User", type="primary"):
                                if database.activate_user(user_id):
                                    st.success("User activated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to activate user")
                        else:
                            st.info("User is already active")
            else:
                st.info("No users available")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")

    # Role definitions
    st.subheader("📋 Role Definitions")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Admin:**
        - Full access to all pages
        - Can create/edit users, customers, platforms
        - Can import requirements
        - Can modify system settings
        """)
    with col2:
        st.markdown("""
        **Visitor:**
        - Read-only access to Status, Dashboard, TableView, Matching, Trace, Reports
        - Cannot access Import pages or Admin panel
        - Cannot modify data
        """)

# ============================================================================
# TAB 2: CUSTOMER MANAGEMENT
# ============================================================================
with tab2:
    st.subheader("Customer Management")

    # List customers
    try:
        customers = database.list_customers()
        if customers:
            df = pd.DataFrame(customers)
            display_cols = ['customer_id', 'name', 'status', 'created_at']
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("No customers found.")
    except Exception as e:
        st.error(f"Error loading customers: {e}")

    st.markdown("---")

    # Create new customer
    with st.expander("➕ Create New Customer"):
        with st.form("create_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_id = st.text_input("Customer ID*", help="e.g., A, B, C (will be prefixed with 'Customer_')")
            with col2:
                customer_name = st.text_input("Customer Name*", help="Display name for the customer")

            col3, col4 = st.columns(2)
            with col3:
                industry = st.text_input("Industry", help="e.g., Automotive, Aerospace")
            with col4:
                description = st.text_area("Description", height=68)

            if st.form_submit_button("Create Customer", type="primary"):
                if not customer_id or not customer_name:
                    st.error("Customer ID and Name are required")
                else:
                    result = database.create_customer(customer_id, customer_name, description, industry)
                    if result.get("status") == "success":
                        st.success(f"Customer '{result.get('customer_id')}' created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create customer: {result.get('message')}")

    # Delete customer
    with st.expander("🗑️ Delete Customer"):
        try:
            customers = database.list_customers()
            if customers:
                customer_options = {c['customer_id']: c['customer_id'] for c in customers}
                selected_customer = st.selectbox("Select Customer to Delete", list(customer_options.keys()), key="delete_customer_select")

                st.warning("Warning: This action cannot be undone!")

                if st.button("Delete Customer", type="secondary", key="delete_customer_btn"):
                    result = database.delete_customer(selected_customer)
                    if result.get("status") == "success":
                        st.success(f"Customer {selected_customer} deleted!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete: {result.get('message')}")
            else:
                st.info("No customers to delete")
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================================================
# TAB 3: PLATFORM MANAGEMENT
# ============================================================================
with tab3:
    st.subheader("Platform Management")

    # List platforms
    try:
        platforms = database.list_platforms()
        if platforms:
            df = pd.DataFrame(platforms)
            display_cols = ['platform_id', 'name', 'version', 'status', 'created_at']
            display_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("No platforms found.")
    except Exception as e:
        st.error(f"Error loading platforms: {e}")

    st.markdown("---")

    # Create new platform
    with st.expander("➕ Create New Platform"):
        with st.form("create_platform_form"):
            col1, col2 = st.columns(2)
            with col1:
                platform_id = st.text_input("Platform ID*", help="e.g., A, B, C (will be prefixed with 'Platform_')")
                version = st.text_input("Version", value="1.0")
            with col2:
                platform_name = st.text_input("Platform Name*", help="Display name for the platform")
                status = st.selectbox("Status", ["Active", "Development", "Archived"])

            if st.form_submit_button("Create Platform", type="primary"):
                if not platform_id or not platform_name:
                    st.error("Platform ID and Name are required")
                else:
                    result = database.create_platform(platform_id, platform_name, version, status)
                    if result.get("status") == "success":
                        st.success(f"Platform '{result.get('platform_id')}' created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create platform: {result.get('message')}")

    # Update platform
    with st.expander("✏️ Update Platform"):
        try:
            platforms = database.list_platforms()
            if platforms:
                platform_options = {p['platform_id']: p for p in platforms}
                selected_platform = st.selectbox("Select Platform", list(platform_options.keys()), key="update_platform_select")

                if selected_platform:
                    current = platform_options[selected_platform]
                    st.write(f"**Current version:** {current.get('version', 'N/A')}")
                    st.write(f"**Current status:** {current.get('status', 'N/A')}")

                    with st.form("update_platform_form"):
                        new_version = st.text_input("New Version", value=current.get('version', ''))
                        new_status = st.selectbox("New Status", ["Active", "Development", "Archived"],
                                                  index=["Active", "Development", "Archived"].index(current.get('status', 'Active')) if current.get('status') in ["Active", "Development", "Archived"] else 0)

                        if st.form_submit_button("Update Platform"):
                            if database.update_platform(selected_platform, status=new_status, version=new_version):
                                st.success("Platform updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update platform")
            else:
                st.info("No platforms to update")
        except Exception as e:
            st.error(f"Error: {e}")

    # Delete platform
    with st.expander("🗑️ Delete Platform"):
        try:
            platforms = database.list_platforms()
            if platforms:
                platform_options = {p['platform_id']: p['platform_id'] for p in platforms}
                selected_platform = st.selectbox("Select Platform to Delete", list(platform_options.keys()), key="delete_platform_select")

                st.warning("Warning: This action cannot be undone!")

                if st.button("Delete Platform", type="secondary", key="delete_platform_btn"):
                    result = database.delete_platform(selected_platform)
                    if result.get("status") == "success":
                        st.success(f"Platform {selected_platform} deleted!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete: {result.get('message')}")
            else:
                st.info("No platforms to delete")
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================================================
# TAB 4: SYSTEM SETTINGS
# ============================================================================
with tab4:
    st.subheader("System Settings")
    st.info("System configuration options will be implemented in future versions.")

    st.markdown("### 📊 Current System Info")

    try:
        users = database.list_all_users()
        customers = database.list_customers()
        platforms = database.list_platforms()
        agents = database.list_agent_status()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", len(users) if users else 0)
        with col2:
            st.metric("Total Customers", len(customers) if customers else 0)
        with col3:
            st.metric("Total Platforms", len(platforms) if platforms else 0)
        with col4:
            st.metric("Active Agents", len([a for a in agents if a.get('status') == 'READY']) if agents else 0)

        st.markdown("---")

        st.markdown("### 📋 Available Roles")
        roles = database.get_available_roles()
        if roles:
            for role in roles:
                st.write(f"- **{role['name']}** (ID: {role['role_id']})")
        else:
            st.info("No roles found")

    except Exception as e:
        st.error(f"Error loading system info: {e}")
