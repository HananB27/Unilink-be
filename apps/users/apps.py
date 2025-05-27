import os

from django.apps import AppConfig
from neomodel import config

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'

    def ready(self):
        neo4j_user = os.environ.get('NEO4J_USERNAME')
        neo4j_password = os.environ.get('NEO4J_PASSWORD')
        neo4j_uri = os.environ.get('NEO4J_URI')
        host = os.environ.get('NEO4J_URI', '').replace('neo4j+s://', '')
        config.DATABASE_URL =f"bolt+s://{neo4j_user}:{neo4j_password}@{host}"

        print(f"[NEO4J CONFIG] Connected to {config.DATABASE_URL}")
