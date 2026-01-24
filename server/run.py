from os import environ

from app import create_app

app = create_app()


if __name__ == '__main__':
    app.run(host=environ.get('HOST'), port=environ.get('BACKEND_PORT'), debug=True)
