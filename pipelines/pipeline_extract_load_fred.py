import pandas as pd
import logging
from datetime import datetime

from config.db import get_engine

from etl.extract.incremental.fred_incremental import fetch_series
from etl.load.load_fred_incremental import get_max_date_by_series, insert_new_records

# ─── Configuração ────────────────────────────────────────────────────────────


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


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

def get_observation_start(series:str, max_dates:dict) -> str:

    max_date = max_dates.get(series)

    if max_date is None:
        logger.warning(f'[{series}] Série não encontrada no banco. Usando fallback: {HISTORICAL_FALLBACK}')
        return HISTORICAL_FALLBACK
    
    max_date = pd.to_datetime(max_date)
    return (max_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')



def run():
    """
    Executa a carga incremental para todas as séries configuradas.
    Cada série avança a partir do seu próprio max_date.
    """

    engine = get_engine()


    logger.info('Iniciando a carga incremental do FRED...')
    
    max_dates = get_max_date_by_series(engine)

    logger.info(f'Datas encontradas: {max_dates}')


    run_summary = []

    for series_id, meta in SERIES_CONFIG.items():

        observation_start = get_observation_start(series_id, max_dates)

        logger.info(f'[{series_id}] Buscando a partir de {observation_start} ({meta["frequency"]})...')


        df_new = fetch_series(series_id, observation_start)
        records_inserted = insert_new_records(df_new, engine)


        logger.info(f'[{series_id}] {records_inserted} novos registros.')

        run_summary.append({
            'series_id':         series_id,
            'observation_start': observation_start,
            'records_inserted':  records_inserted,
            'run_at':            datetime.now().isoformat(),
            'status':            'success' if records_inserted >= 0 else 'error',
        })


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


if __name__ == '__main__':
    run()