import requests
import pandas as pd
from dotenv import load_dotenv
import pyarrow
import os
import logging
from datetime import datetime
from config.paths import BASE_DIR


# ─── Configuração ────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv('API_KEY_FRED')

BASE_URL = 'https://api.stlouisfed.org/fred/'

ENDPOINT = 'series/observations'

file_path = BASE_DIR / 'data' / 'raw' / 'fred' / 'fred_data.parquet'


SERIES_CONFIG = {
    'FEDFUNDS': {'frequency': 'monthly',   'description': 'Fed Funds Rate'},
    'CPIAUCSL': {'frequency': 'monthly',   'description': 'CPI Inflation'},
    'UNRATE':   {'frequency': 'monthly',   'description': 'Unemployment Rate'},
    'GDPC1':    {'frequency': 'quarterly', 'description': 'Real GDP'},
    'M2SL':     {'frequency': 'monthly',   'description': 'M2 Money Supply'},
    'DGS10':    {'frequency': 'daily',     'description': '10Y Treasury Yield'},
}

HISTORICAL_FALLBACK = '2018-01-01'


# ─── Funções ────────────────────────────────────────────────────────────

def get_max_date_by_series(df: pd.DataFrame, series_id: str) -> str:
    """
    Retorna a data de início para a busca incremental de uma série específica.
    Se a série ainda não existir no parquet, retorna o fallback histórico.
    """

    series_df = df[df['series'] == series_id]

    if series_df.empty:
        logger.info(f"Série {series_id} não encontrada. Usando fallback histórico: {HISTORICAL_FALLBACK}")
        return HISTORICAL_FALLBACK

    max_date = pd.to_datetime(series_df['date'].max(), utc=True)
    next_date = (max_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    logger.info(f"Serie encontrada: {series_id}, data de busca incremental: {next_date}")

    return next_date



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


    return new_df


def run_incremental():
    """
    Executa a carga incremental para todas as séries configuradas.
    Cada série avança a partir do seu próprio max_date.
    """

    logger.info('Iniciando a carga incremental do FRED...')

    df = pd.read_parquet(file_path, engine='pyarrow')

    new_frames = []
    run_summary = []

    for series_id, meta in SERIES_CONFIG.items():
        
        observation_start = get_max_date_by_series(df, series_id)

        logger.info(f'[{series_id}] Buscando a partir de {observation_start} ({meta["frequency"]})...')


        new_df = fetch_series(series_id, observation_start)
        records_inserted = len(new_df)

        if not new_df.empty:
            new_frames.append(new_df)

        logger.info(f'[{series_id}] {records_inserted} novos registros.')

        run_summary.append({
            'series_id':         series_id,
            'observation_start': observation_start,
            'records_inserted':  records_inserted,
            'run_at':            datetime.now().isoformat(),
            'status':            'success' if records_inserted >= 0 else 'error',
        })



    if not new_frames:
        logger.info('Nenhum dado novo encontrado. Parquet não alterado.')
        _log_summary(run_summary)
        return


    df_combined = pd.concat([df] + new_frames, ignore_index=True)

    df_combined.to_parquet(file_path, engine='pyarrow', index=False)
    logger.info(f'Parquet atualizado — {len(df_combined)} registros totais.')

    _log_summary(run_summary)



def _log_summary(summary: list[dict]):
    """Imprime um resumo da execução por série."""
    logger.info('─── Resumo da execução ───────────────────────────────')
    for row in summary:
        logger.info(
            f'  {row["series_id"]:<10} | início: {row["observation_start"]} '
            f'| inseridos: {row["records_inserted"]:>4} | status: {row["status"]}'
        )
    logger.info('──────────────────────────────────────────────────────')





# ─── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    run_incremental()