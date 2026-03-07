from server.app import create_app
from server.app.extensions import db
from server.app.models.location_model import LocationModel

app = create_app()
app.app_context().push()

print("Location count:", LocationModel.query.count())
