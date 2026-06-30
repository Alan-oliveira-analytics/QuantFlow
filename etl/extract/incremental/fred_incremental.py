import requests
import pandas as pd
import os
import logging
from dotenv import load_dotenv
from config.paths import ENV_PATH
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── Configuração ────────────────────────────────────────────────────────────


logger = logging.getLogger(__name__)

BASE_URL = 'https://api.stlouisfed.org/fred/'

ENDPOINT = 'series/observations'


# ─── Funções ────────────────────────────────────────────────────────────


def _build_session() -> requests.Session:
    retry = Retry(
        total=3,                       # até 3 tentativas
        backoff_factor=1,              # espera 1s, 2s, 4s... entre elas
        status_forcelist=[429, 500, 502, 503, 504],  # também re-tenta erros de servidor
        allowed_methods=['GET'],
    )
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry))
    return session


def fetch_series(series_id, observation_start:str, session) -> pd.DataFrame:
    """
    Busca novas observações de uma série FRED a partir de uma data.
    Retorna DataFrame vazio se não houver dados novos.
    """

    load_dotenv(ENV_PATH)

    API_KEY = os.getenv('API_KEY_FRED')

    observation_end = pd.to_datetime('today').strftime('%Y-%m-%d')


    params = {
        'api_key': f'{API_KEY}',
        'file_type': 'json',
        'observation_start': observation_start,
        'observation_end': observation_end,
        'series_id': series_id
    }


    try:
        response = session.get(f'{BASE_URL}{ENDPOINT}', params=params, timeout=(10, 30))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        msg = str(e).replace(API_KEY, '*****') if API_KEY else str(e)
        logger.error(f'[{series_id}] Erro na requisição: {msg}')
        return 'error', pd.DataFrame()


    observations = response.json().get('observations', [])    
    
    new_df = pd.DataFrame(observations)
    new_df['series'] = series_id

    # Garante que só entram datas estritamente posteriores ao max_date do banco
    new_df['date'] = pd.to_datetime(new_df['date'])
    new_df = new_df[new_df['date'] > pd.to_datetime(observation_start)]

    if new_df.empty:
        logger.info(f'[{series_id}] Nenhum dado novo desde {observation_start}.')
        return 'no_data', pd.DataFrame()

    return 'success', new_df

