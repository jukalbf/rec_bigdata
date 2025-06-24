import pandas as pd
from database.mongo_db import MongoDB
import logging
import numpy as np
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.path.exists('data/raw/medicamentos.csv'):
    logger.error("Arquivo CSV não encontrado!")
    exit(1)

def run_etl():
    try:
        df = pd.read_csv('data/raw/medicamentos.csv', encoding='latin1', sep=';')

        df = df.rename(columns={
            'distrito': 'distrito',
            'bairro': 'bairro',
            'unidade': 'unidade',
            'produto': 'medicamento',
            'quantidade': 'quantidade_str',
            'data_carga': 'data_carga'
        })

        df['quantidade'] = df['quantidade_str'].str.replace(',', '.').replace('', np.nan).astype(float)

        cols_manter = ['distrito', 'bairro', 'unidade', 'medicamento', 'quantidade', 'data_carga']
        df = df[[col for col in cols_manter if col in df.columns]]

        metrics = {}

        if 'medicamento' in df.columns and 'quantidade' in df.columns:
            medicamentos_populares = (
                df.groupby('medicamento')['quantidade']
                .sum()
                .nlargest(10)
                .reset_index(name='total')
            )
            metrics['medicamentos_populares'] = medicamentos_populares.to_dict('list')

        if 'bairro' in df.columns and 'quantidade' in df.columns:
            distribuicao_bairros = df.groupby('bairro')['quantidade'].sum().reset_index(name='total')
            metrics['distribuicao_bairros'] = distribuicao_bairros.to_dict('list')

        db = MongoDB()
        db.insert_data('distribuicao_medicamentos', df.to_dict('records'))

        if metrics:
            db.insert_data('metricas_saude', metrics)

        db.close()
        logging.info("ETL de saúde concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro no ETL de saúde: {str(e)}")

if __name__ == "__main__":
    run_etl()
