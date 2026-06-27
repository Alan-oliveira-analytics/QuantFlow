import pandas as pd
import logging
from datetime import datetime

from config.db import get_engine
from config.settings import HISTORICAL_FALLBACK

from etl.extract.incremental.yahoo import extract_yfinance_data
from etl.load.load_yahoo_incremental import get_max_date, insert_new_records

# ─── Configuração ────────────────────────────────────────────────────────────


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


# ─── Funções ────────────────────────────────────────────────────────────



def run():
    """
    Executa a carga incremental a partir do max_date.
    """

    engine = get_engine()


    logger.info('Iniciando a carga incremental do yFinance...')
    
    max_date = get_max_date(engine)
    
    if pd.isna(max_date):
        logger.warning(f'Data não encontrada no banco. Usando fallback: {HISTORICAL_FALLBACK}')
        next_date = pd.Timestamp(HISTORICAL_FALLBACK)
    else:
        next_date = max_date + pd.Timedelta(days=1)


    logger.info(f'Data para extração dos novos dados: {next_date}')


    df = extract_yfinance_data(next_date)

    records_inserted = insert_new_records(df, engine)

    logger.info(f'{records_inserted} novos registros.')



if __name__ == '__main__':
    run()