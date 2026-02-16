# application.py (located in your root folder)

from app import app as application

# If your Flask variable inside app.py is named 'app', 
# this line imports it and renames it to 'application' 
# so AWS can find it automatically.

if __name__ == "__main__":
    application.run()