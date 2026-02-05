import os
from dotenv import load_dotenv
from app import create_app, db
from flask_migrate import Migrate

# Load .env variables
load_dotenv()

# Create app and initialize Flask-Migrate
app = create_app()
migrate = Migrate(app, db)

# Expose app for CLI
if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("BACKEND_PORT", 5000)),
            debug=os.environ.get("DEBUG", "True") == "True")
