from sqlalchemy.ext.declarative import declarative_base
import core.config as config
import os

Base = declarative_base()

database = config.DB
user = config.DB_USER
pw = config.DB_PASSWORD
server = config.DB_SERVER
port = config.DB_PORT
name = config.DB_NAME
DATABASE_URL = os.getenv('DATABASE_URL', f'{database}://{user}:{pw}@{server}:{port}/{name}')

