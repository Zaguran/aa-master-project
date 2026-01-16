import streamlit as st
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from components import security, session


def get_connection():
    """Get database connection to work_aa schema."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT'),
        options="-c search_path=work_aa"
    )


def login(email: str, password: str) -> bool:
    """
    Authenticate user and create session.
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        True if login successful, False otherwise
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user by email
        cur.execute("""
            SELECT 
                u.user_id,
                u.email,
                u.full_name,
                u.password_hash,
                u.is_active,
                ARRAY_AGG(r.name) as roles
            FROM app_user u
            LEFT JOIN app_user_role ur ON u.user_id = ur.user_id
            LEFT JOIN app_role r ON ur.role_id = r.role_id
            WHERE u.email = %s
            GROUP BY u.user_id, u.email, u.full_name, u.password_hash, u.is_active;
        """, (email,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return False
        
        if not user['is_active']:
            return False
        
        # Verify password
        if not security.verify_password(password, user['password_hash']):
            return False
        
        # Create session
        session_data = session.create_session(str(user['user_id']))
        if not session_data:
            return False
        
        # Store in session state
        st.session_state.authenticated = True
        st.session_state.session_id = session_data['session_id']
        st.session_state.user = {
            'user_id': str(user['user_id']),
            'email': user['email'],
            'full_name': user['full_name'],
            'roles': [r for r in user['roles'] if r is not None]
        }
        
        return True
        
    except Exception as e:
        st.error(f'Debug DB Error: {e}')
        print(f"Login error: {e}")
        return False


def logout():
    """Logout current user and revoke session."""
    if st.session_state.get('session_id'):
        session.revoke_session(st.session_state.session_id)
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.session_id = None


def get_current_user() -> dict:
    """
    Get current authenticated user.
    
    Returns:
        User dictionary or None if not authenticated
    """
    if not st.session_state.get('authenticated'):
        return None
    
    if not st.session_state.get('session_id'):
        return None
    
    # Validate session is still valid
    if not session.validate_session(st.session_state.session_id):
        logout()
        return None
    
    return st.session_state.get('user')


def require_role(roles: list):
    """
    Require user to have one of the specified roles.
    Shows error and stops execution if user doesn't have required role.
    
    Args:
        roles: List of role names (e.g., ['admin', 'visitor'])
    """
    user = get_current_user()
    
    if not user:
        st.error("Access denied. Please login.")
        st.stop()
    
    user_roles = user.get('roles', [])
    
    if not any(role in user_roles for role in roles):
        st.error(f"Access denied. Required role: {', '.join(roles)}")
        st.stop()


def is_authenticated() -> bool:
    """
    Check if user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return get_current_user() is not None


def has_role(role: str) -> bool:
    """
    Check if current user has specific role.
    
    Args:
        role: Role name to check
        
    Returns:
        True if user has role, False otherwise
    """
    user = get_current_user()
    if not user:
        return False
    return role in user.get('roles', [])
