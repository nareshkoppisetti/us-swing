"""
File path: backend/scripts/seed_admin_user.py
Purpose: Create (or reset) the first super_admin user so you can log in.

There are only two roles in this app: "admin" and "user".

Usage:
    cd backend
    source venv/bin/activate   # Windows: venv\\Scripts\\activate

    # create/reset an admin account
    python scripts/seed_admin_user.py --username admin --email admin@example.com --password ChangeMe123! --role admin

    # create/reset a normal user account
    python scripts/seed_admin_user.py --username john --email john@example.com --password ChangeMe123! --role user

If the username already exists, its password/role is reset instead of erroring
out, so this script is safe to re-run any time you get locked out.

Add --list to print all existing accounts and their roles:
    python scripts/seed_admin_user.py --list
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, init_db
from core.security import hash_password
from modules.auth.models import User


def main():
    parser = argparse.ArgumentParser(description="Seed / reset the first admin user")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--email", default="admin@usaswing.local")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--role", default="admin", choices=["admin", "user"])
    parser.add_argument("--list", action="store_true",
                         help="List all existing users and their roles, then exit.")
    args = parser.parse_args()

    # Make sure all tables exist (safe no-op if they already do)
    init_db()

    db = SessionLocal()

    if args.list:
        try:
            users = db.query(User).order_by(User.created_at).all()
            if not users:
                print("No users exist yet.")
            for u in users:
                status = "active" if u.is_active else "disabled"
                print(f"{u.username:20s} {u.email:30s} role={u.role:6s} {status}")
        finally:
            db.close()
        return

    try:
        user = db.query(User).filter(User.username == args.username).first()
        if user:
            user.hashed_password = hash_password(args.password)
            user.role = args.role
            user.is_active = True
            action = "Reset password for"
        else:
            user = User(
                username=args.username,
                email=args.email,
                hashed_password=hash_password(args.password),
                role=args.role,
                is_active=True,
            )
            db.add(user)
            action = "Created"

        db.commit()
        print(f"{action} user '{args.username}' (role={args.role}).")
        print(f"Login with username='{args.username}' password='{args.password}'")
    finally:
        db.close()


if __name__ == "__main__":
    main()
