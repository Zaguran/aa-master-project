import streamlit as st
from datetime import datetime, timedelta
import uuid
from components import security
import os
import psycopg2
from psycopg2.extras import RealDictCursor


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


def create_session(user_id: str) -> dict:
    """
    Create a new session in database and return session data.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        Dictionary with session_id and csrf_token
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        csrf_token = security.generate_csrf_token()
        expires_at = datetime.now() + timedelta(hours=8)
        
        cur.execute("""
            INSERT INTO app_session (user_id, expires_at, csrf_token, revoked)
            VALUES (%s, %s, %s, FALSE)
            RETURNING session_id, csrf_token;
        """, (user_id, expires_at, csrf_token))
        
        session = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'session_id': str(session['session_id']),
            'csrf_token': session['csrf_token']
        }
    except Exception as e:
        print(f"Error creating session: {e}")
        return None


def validate_session(session_id: str) -> bool:
    """
    Validate if session exists and is not expired or revoked.
    
    Args:
        session_id: Session UUID to validate
        
    Returns:
        True if session is valid, False otherwise
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT session_id, expires_at, revoked
            FROM app_session
            WHERE session_id = %s;
        """, (session_id,))
        
        session = cur.fetchone()
        cur.close()
        conn.close()
        
        if not session:
            return False
        
        if session['revoked']:
            return False
        
        if datetime.now() > session['expires_at']:
            return False
        
        return True
    except Exception as e:
        print(f"Error validating session: {e}")
        return False


def revoke_session(session_id: str):
    """
    Revoke a session (logout).
    
    Args:
        session_id: Session UUID to revoke
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE app_session
            SET revoked = TRUE
            WHERE session_id = %s;
        """, (session_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error revoking session: {e}")


def get_user_from_session(session_id: str) -> dict:
    """
    Get user data from session ID.
    
    Args:
        session_id: Session UUID
        
    Returns:
        Dictionary with user data and roles, or None if invalid
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                u.user_id,
                u.email,
                u.full_name,
                u.is_active,
                ARRAY_AGG(r.name) as roles
            FROM app_session s
            JOIN app_user u ON s.user_id = u.user_id
            LEFT JOIN app_user_role ur ON u.user_id = ur.user_id
            LEFT JOIN app_role r ON ur.role_id = r.role_id
            WHERE s.session_id = %s
                AND s.revoked = FALSE
                AND s.expires_at > NOW()
            GROUP BY u.user_id, u.email, u.full_name, u.is_active;
        """, (session_id,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return {
                'user_id': str(user['user_id']),
                'email': user['email'],
                'full_name': user['full_name'],
                'is_active': user['is_active'],
                'roles': [r for r in user['roles'] if r is not None]
            }
        return None
    except Exception as e:
        print(f"Error getting user from session: {e}")
        return None


def init_session_state():
    """Initialize session state variables if not present."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
