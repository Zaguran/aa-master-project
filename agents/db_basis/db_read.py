#!/usr/bin/env python3
"""
DB Inspection Script - Read and display contents of work_aa schema tables
"""
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


def inspect_app_user():
    """Inspect app_user table - show email, full_name, is_active."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT user_id, email, full_name, is_active FROM app_user")
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*80}")
        print(f"TABLE: app_user")
        print(f"{'='*80}")
        
        if rows:
            for row in rows:
                print(f"User ID: {row['user_id']}")
                print(f"  Email: {row['email']}")
                print(f"  Full Name: {row['full_name']}")
                print(f"  Active: {row['is_active']}")
                print("-" * 80)
            print(f"Total users: {len(rows)}")
        else:
            print("No users found.")
        
    except Exception as e:
        print(f"ERROR inspecting app_user: {e}")


def inspect_app_user_role():
    """Inspect app_user_role table - show user_id and role_id."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT ur.user_id, ur.role_id, r.name as role_name
            FROM app_user_role ur
            LEFT JOIN app_role r ON ur.role_id = r.role_id
        """)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*80}")
        print(f"TABLE: app_user_role")
        print(f"{'='*80}")
        
        if rows:
            for row in rows:
                print(f"User ID: {row['user_id']} -> Role ID: {row['role_id']} ({row['role_name']})")
            print("-" * 80)
            print(f"Total role assignments: {len(rows)}")
        else:
            print("No role assignments found.")
        
    except Exception as e:
        print(f"ERROR inspecting app_user_role: {e}")


def inspect_app_session():
    """Inspect app_session table - show session_id, user_id, expires_at (newest first)."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT session_id, user_id, expires_at, created_at, revoked
            FROM app_session
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*80}")
        print(f"TABLE: app_session (newest first)")
        print(f"{'='*80}")
        
        if rows:
            for row in rows:
                print(f"Session ID: {row['session_id']}")
                print(f"  User ID: {row['user_id']}")
                print(f"  Created: {row['created_at']}")
                print(f"  Expires: {row['expires_at']}")
                print(f"  Revoked: {row['revoked']}")
                print("-" * 80)
            print(f"Total sessions: {len(rows)}")
        else:
            print("No sessions found.")
        
    except Exception as e:
        print(f"ERROR inspecting app_session: {e}")


def main():
    """Main inspection routine."""
    print("\n" + "="*80)
    print("DB INSPECTION SCRIPT - work_aa schema")
    print("="*80)
    
    # Inspect app_user
    inspect_app_user()
    
    # Inspect app_user_role
    inspect_app_user_role()
    
    # Inspect app_session (ordered by created_at DESC)
    inspect_app_session()
    
    print("\n" + "="*80)
    print("INSPECTION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
