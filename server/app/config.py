# Import environment variables

import os

from dotenv import load_dotenv

# Load environment variables from a .env file into the system's environment variables
load_dotenv()

config_dict = os.environ

class Config:

    SECRET_KEY = None
    DB_URI = None

    def get_config(self):

        DB_NAME = config_dict.get('DB_NAME')
        DB_USERNAME = config_dict.get('DB_USERNAME')
        DB_PASSWORD = config_dict.get('DB_PASSWORD')
        DB_HOST = config_dict.get('DB_HOST')
        DB_PORT = config_dict.get('DB_PORT')

        self.SECRET_KEY = config_dict.get('SECRET_KEY')

        self.DB_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

        if any(attr is None for attr in [self.SECRET_KEY, self.DB_URI, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT]):
            raise ValueError("One or more required environment variables are missing.")