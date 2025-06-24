import pandas as pd
from database.mongo_db import MongoDB
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.path.exists('data/raw/roteirizacao.csv'):
    logger.error("Arquivo CSV não encontrado!")
    exit(1)

def run_etl():
    try:
        df = pd.read_csv('data/raw/roteirizacao.csv', encoding='latin1', sep=';')

        df = df.rename(columns={
            'intervalo': 'intervalo',
            'setor': 'setor',
            'endereco': 'endereco',
            'turno': 'turno',
            'rota_setor': 'rota_setor',
            'frequencia': 'frequencia'
        })

        metrics = {}

        if 'setor' in df.columns:
            rotas_por_setor = df.groupby('setor').size().reset_index(name='total')
            metrics['rotas_por_setor'] = rotas_por_setor.to_dict('list')

        if 'turno' in df.columns:
            rotas_por_turno = df['turno'].value_counts().reset_index()
            rotas_por_turno.columns = ['turno', 'total']
            metrics['rotas_por_turno'] = rotas_por_turno.to_dict('list')

        db = MongoDB()
        db.insert_data('limpeza_urbana', df.to_dict('records'))

        if metrics:
            db.insert_data('metricas_limpeza', metrics)

        db.close()
        logging.info("ETL de limpeza urbana concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro no ETL de limpeza urbana: {str(e)}")

if __name__ == "__main__":
    run_etl()
