from pymongo import MongoClient
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class MongoDB:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/recife_dados")

        if "mongodb+srv" in self.uri:
            db_start = self.uri.rfind("/") + 1
            db_end = self.uri.find("?", db_start)
            self.db_name = self.uri[db_start:db_end] if db_end != -1 else self.uri[db_start:]
        else:
            self.db_name = self.uri.split("/")[-1].split("?")[0]

        safe_uri = self.uri.split("@")[-1] if "@" in self.uri else self.uri
        print(f"Conectando ao MongoDB: {safe_uri}")

        try:
            self.client = MongoClient(self.uri)
            self.client.server_info()
            self.db = self.client[self.db_name]
            print(f"Conexão bem-sucedida com o banco '{self.db_name}'")
        except Exception as e:
            print(f"ERRO: Falha na conexão com MongoDB: {str(e)}")
            print("Usando banco de dados em memória (dados serão perdidos após execução)")
            self.db = {}

    def get_distinct_values(self, collection_name, field):
            """Obtém valores distintos de um campo em uma coleção"""
            if not hasattr(self, 'client') or not self.client:
                print(f"Simulando valores distintos para {field} em {collection_name}")
                return []

            try:
                collection = self.db[collection_name]
                return collection.distinct(field)
            except Exception as e:
                print(f"Erro ao obter valores distintos: {str(e)}")
                return []

    def insert_data(self, collection_name, data):
        if not hasattr(self, 'client') or not self.client:
            print(f"Simulando inserção em {collection_name} ({len(data) if isinstance(data, list) else 1} documentos)")
            return

        try:
            collection = self.db[collection_name]
            if isinstance(data, list):
                result = collection.insert_many(data)
                print(f"{len(result.inserted_ids)} documentos inseridos em {collection_name}")
            else:
                result = collection.insert_one(data)
                print(f"1 documento inserido em {collection_name}")
        except Exception as e:
            print(f"Erro ao inserir em {collection_name}: {str(e)}")

    def get_data(self, collection_name, query={}):
        if not hasattr(self, 'client') or not self.client:
            print(f"Simulando leitura de {collection_name}")
            return []

        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            print(f"Erro ao ler {collection_name}: {str(e)}")
            return []

    def close(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()
            print("Conexão com MongoDB fechada")

if __name__ == "__main__":
    db = MongoDB()
    print("Coleções disponíveis:", db.db.list_collection_names() if hasattr(db, 'db') else "Nenhuma")

    print("Bairros distintos:", db.get_distinct_values('ocorrencias_seguranca', 'bairro'))

    db.close()
