from server.app.models import user_account_model, edges_model, nodes_model, missions_model
from server.app.models.enums.ACCESS_TYPE import UserAccessType as access
from server.app.models.enums.MISSION_TIER import MissionTier as mission_tier

from app.extensions import db

user = user_account_model.UserAccountModel(
    username = "Active User",
    email = "admin@test.com",
    password_hash = "password",
    role = access.TRAVELLERS,
)

print("Inserting User")
db.session.add(user)
db.session.commit()