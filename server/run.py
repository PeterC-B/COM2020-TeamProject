#from os import environ

#from app import create_app

#app = create_app()


#if __name__ == '__main__':
#    app.run(host=environ.get('HOST'), port=environ.get('BACKEND_PORT'), debug=True)

#import os
#from app import create_app

#app = create_app()

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8000))
 #   host = "0.0.0.0"
 #   debug = os.environ.get("DEBUG", "False") == "True"
#    app.run(host=host, port=port, debug=debug)

from app import create_app

app = create_app()

