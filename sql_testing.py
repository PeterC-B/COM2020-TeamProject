from server.app import create_app
from server.app.extensions import db
from server.app.models import user_account_model, missions_model
from server.app.models.enums.ACCESS_TYPE import UserAccessType as access
from server.app.models.enums.MISSION_TIER import MissionTier as tier
from sqlalchemy import inspect


# Create Flask app properly
app = create_app()

def insert_user():
    user = user_account_model.UserAccountModel(
        username="maxChambers",
        email="mc1276@exeter.ac.uk",
        password_hash="password",  # see note below
        role=access.MAINTAINERS,
    )

    print("Inserting user...")
    db.session.add(user)
    db.session.commit()
    print("User inserted successfully")

def select_all_users():
    print("\nSelecting all users...")


    active_users = (
        db.session
        .query(user_account_model.UserAccountModel)
        .all()
    )


    for u in active_users:
        print(u.id, u.email, u.password_hash)

def insert_mission():
    mission = missions_model.MissionsModel(
        mission_name="Least crossings",
        question="Why is it good to avoid crossings?",
        answer="So you don't get turned into jam",
        tier=tier.HARD,
    )

    print("Inserting mission...")
    db.session.add(mission)
    db.session.commit()
    print("Mission inserted successfully")

def query_mission():
    print("\nSelecting all missions...")


    missions = (
        db.session
        .query(missions_model.MissionsModel)
        .all()
    )


    for u in missions:
        print(u.mission_id, u.mission_name, u.question, u.answer, u.tier)

with app.app_context():
    query_mission()