import pandas as pd
from database.mongo_db import MongoDB
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.path.exists('data/raw/sedec2023.csv'):
    logger.error("Arquivo CSV não encontrado!")
    exit(1)

def run_etl():
    try:
        df = pd.read_csv(
            'data/raw/sedec2023.csv',
            encoding='latin1',
            sep=';',
            on_bad_lines='skip',
            dtype=str
        )

        df = df.rename(columns={
            'Regional': 'regional',
            'Data': 'data',
            'Ocorrencia': 'ocorrencia',
            'Bairro': 'bairro',
            'Tipo_da_Acao': 'tipo_acao',
            'Situacao': 'situacao'
        })

        cols_manter = ['regional', 'data', 'ocorrencia', 'bairro', 'tipo_acao', 'situacao']
        df = df[[col for col in cols_manter if col in df.columns]]

        metrics = {}

        if 'bairro' in df.columns:
            ocorrencias_bairro = df.groupby('bairro').size().reset_index(name='total')
            metrics['por_bairro'] = ocorrencias_bairro.to_dict('list')

        if 'tipo_acao' in df.columns:
            ocorrencias_tipo = df['tipo_acao'].value_counts().reset_index()
            ocorrencias_tipo.columns = ['tipo_acao', 'total']
            metrics['por_tipo'] = ocorrencias_tipo.to_dict('list')

        db = MongoDB()
        db.insert_data('ocorrencias_seguranca', df.to_dict('records'))

        if metrics:
            db.insert_data('metricas_seguranca', metrics)

        db.close()
        logging.info("ETL de segurança pública concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro no ETL de segurança: {str(e)}")

if __name__ == "__main__":
    run_etl()
