# Import environment variables

import os

from dotenv import load_dotenv

from app.domain.errors import ValidationError

# Load environment variables from a .env file into the system's environment variables
load_dotenv()

config_dict = os.environ

class Config:

    APP_ENV = None
    SECRET_KEY = None
    DB_URI = None
    CORS_ADDRESSES = None

    def get_config(self):

        env = config_dict.get('ENV')
        if env == 'production':
            self.APP_ENV = 'PROD'
            print("App started in Production environment")
        elif env == 'development':
            self.APP_ENV = 'DEV'
            print("App started in Development environment")
        elif env == 'testing':
            self.APP_ENV = 'TEST'
            print("App started in Testing environment")
        else:
            raise ValidationError(
                message="Invalid environment",
                details={"field": "ENV", "allowed": ["development", "testing", "production"]},
            )

        self.SECRET_KEY = config_dict.get('SECRET_KEY')

        DB_NAME = config_dict.get(f'{self.APP_ENV}_DB_NAME')
        DB_USERNAME = config_dict.get(f'{self.APP_ENV}_DB_USERNAME')
        DB_PASSWORD = config_dict.get(f'{self.APP_ENV}_DB_PASSWORD')
        DB_HOST = config_dict.get(f'{self.APP_ENV}_DB_HOST')
        DB_PORT = config_dict.get(f'{self.APP_ENV}_DB_PORT')

        if env == 'production':
            self.DB_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require'
            # print("SSL Enabled")
        else:
            self.DB_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
            # print("SSL Disabled")

        CORS_ADDRESSES = config_dict.get(f'{self.APP_ENV}_CORS_ADDRESSES')
        if not CORS_ADDRESSES:
            raise ValidationError(
                message="Missing required environment variable",
                details={"field": f"{self.APP_ENV}_CORS_ADDRESSES"},
            )
        self.CORS_ADDRESSES = CORS_ADDRESSES.split(',')

        # self.print_config()

        # Check all successfull
        if any(attr is None for attr in [self.APP_ENV, self.SECRET_KEY, self.DB_URI, self.CORS_ADDRESSES]):
            raise ValidationError(message="Error setting up app config")
        

    def print_config(self):
        print("Current Configuration:")
        print(f"SECRET_KEY: {'***' if self.SECRET_KEY else None}")
        print(f"DB_URI: {self.DB_URI}")