from app import create_app
from app.extensions import db
from app.models.location_model import LocationModel

app = create_app()
app.app_context().push()

print("Location count:", LocationModel.query.count())
