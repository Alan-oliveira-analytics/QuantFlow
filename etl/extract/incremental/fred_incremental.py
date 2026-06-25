import requests
import pandas as pd
import os
import logging


# ─── Configuração ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


API_KEY = os.getenv('API_KEY_FRED')

BASE_URL = 'https://api.stlouisfed.org/fred/'

ENDPOINT = 'series/observations'


# ─── Funções ────────────────────────────────────────────────────────────


def fetch_series(series_id, observation_start:str) -> pd.DataFrame:
    """
    Busca novas observações de uma série FRED a partir de uma data.
    Retorna DataFrame vazio se não houver dados novos.
    """

    observation_end = pd.to_datetime('today').strftime('%Y-%m-%d')


    params = {
        'api_key': f'{API_KEY}',
        'file_type': 'json',
        'observation_start': observation_start,
        'observation_end': observation_end,
        'series_id': series_id
    }


    try:
        response = requests.get(f'{BASE_URL}{ENDPOINT}', params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f'[{series_id}] Erro na requisição: {e}')
        return pd.DataFrame()


    observations = response.json().get('observations', [])

    if not observations:
        logger.info(f'[{series_id}] Nenhum dado novo desde {observation_start}.')
        return pd.DataFrame()
    
    new_df = pd.DataFrame(observations)
    new_df['series'] = series_id

    # Garante que só entram datas estritamente posteriores ao max_date do banco
    new_df['date'] = pd.to_datetime(new_df['date'])
    new_df = new_df[new_df['date'] >= pd.to_datetime(observation_start)]



    return new_df

