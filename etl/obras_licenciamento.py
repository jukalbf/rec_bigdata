import pandas as pd
from database.mongo_db import MongoDB
import logging
import os
import chardet

logging.basicConfig(level=logging.INFO)

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
    return result['encoding']

def run_etl():
    try:
        amb_file = 'data/raw/licenciamento_ambiental.csv'
        urb_file = 'data/raw/licenciamento_urbanistico.csv'

        if not os.path.exists(amb_file) or not os.path.exists(urb_file):
            logging.error("Arquivos CSV não encontrados!")
            return

        amb_encoding = detect_encoding(amb_file)
        urb_encoding = detect_encoding(urb_file)
        logging.info(f"Encoding detectado: Ambiental={amb_encoding}, Urbanístico={urb_encoding}")

        try:
            df_amb = pd.read_csv(amb_file, encoding=amb_encoding, sep=';')
        except:
            df_amb = pd.read_csv(amb_file, encoding='utf-8-sig', sep=';')
            logging.warning("Usando fallback utf-8-sig para ambiental")

        try:
            df_urb = pd.read_csv(urb_file, encoding=urb_encoding, sep=';')
        except:
            df_urb = pd.read_csv(urb_file, encoding='utf-8-sig', sep=';')
            logging.warning("Usando fallback utf-8-sig para urbanístico")

        amb_columns = {}
        for col in df_amb.columns:
            clean_col = col.replace('\ufeff', '')
            amb_columns[col] = clean_col

        df_amb = df_amb.rename(columns=amb_columns)

        urb_columns = {}
        for col in df_urb.columns:
            clean_col = col.replace('\ufeff', '')
            urb_columns[col] = clean_col

        df_urb = df_urb.rename(columns=urb_columns)

        # Renomear colunas de conteúdo
        df_amb = df_amb.rename(columns={
            'areatotalconstruida': 'area_total_construida',
            'assunto': 'assunto',
            'bairro': 'bairro',
            'categoria_empreendimento': 'categoria',
            'num_processo': 'processo',
            'tipo_proc_licenciamento': 'tipo_licenciamento'
        })

        df_urb = df_urb.rename(columns={
            'areatotalconstruida': 'area_total_construida',
            'assunto': 'assunto',
            'bairro': 'bairro',
            'categoria_empreendimento': 'categoria',
            'num_processo': 'processo',
            'tipo_proc_licenciamento': 'tipo_licenciamento'
        })

        df_amb['tipo'] = 'Ambiental'
        df_urb['tipo'] = 'Urbanístico'

        df_combined = pd.concat([df_amb, df_urb], ignore_index=True)

        cols_manter = ['bairro', 'processo', 'tipo_licenciamento', 'tipo', 'categoria', 'assunto']
        df_final = df_combined[[col for col in cols_manter if col in df_combined.columns]]

        db = MongoDB()
        db.insert_data('obras_licenciamento', df_final.to_dict('records'))
        db.close()
        logging.info("ETL de obras e licenciamento concluído com sucesso!")

    except Exception as e:
        logging.error(f"Erro no ETL de obras: {str(e)}")

if __name__ == "__main__":
    run_etl()
