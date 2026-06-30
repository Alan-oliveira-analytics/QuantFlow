import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
import logging
from dotenv import load_dotenv
from config.paths import ENV_PATH


logger = logging.getLogger(__name__)


# ─── Conexão com banco ────────────────────────────────────────────────────────────


def get_engine():

    load_dotenv(ENV_PATH)

    url = os.getenv('DATABASE_URL')

    if url:
        # produção
        url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    else:
        # local/desenvolvimento
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        database = os.getenv('POSTGRES_DB')
        host = 'localhost'
        url = f'postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5433/{database}'


    logger.info('Creating database engine...')

    return create_engine(url)