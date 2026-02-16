"""One-time database initialization script.

Creates all SQLAlchemy tables for the configured environment.
"""

from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import select
from werkzeug.security import generate_password_hash

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from server.app.extensions import db
from server.app.models.enums.ACCESS_TYPE import UserAccessType
from server.app.models.user_account_model import UserAccountModel


def main():
    app = create_app()

    with app.app_context():
        print("Creating tables...")
        db.create_all()

        existing_admin = db.session.execute(
            select(UserAccountModel).where(UserAccountModel.role == UserAccessType.ADMINS).limit(1)
        ).scalar_one_or_none()

        if existing_admin is None:
            admin_user = UserAccountModel(
                username="admin",
                email="admin@example.com",
                password_hash="hashed-admin",
                role=UserAccessType.ADMINS,
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username=admin, email=admin@example.com, password=admin (hashed in DB)")
        else:
            print("Admin user already exists; skipping creation.")

        print("Tables initialized successfully.")


if __name__ == "__main__":
    main()
