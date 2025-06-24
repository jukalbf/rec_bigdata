# 🚀 Passo-a-Passo para Executar o Projeto

## Pré-requisitos
- Python 3.10 ou superior instalado
- MongoDB (local ou Atlas)

## Instalação e Execução

1. **Preparar o ambiente:**
```bash
# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install pandas pymongo streamlit plotly python-dotenv chardet
```

2. Configurar o MongoDB:
    * Crie um arquivo `.env` na pasta raiz do projeto com:
    ```
    MONGO_URI=mongodb+srv://<usuário>:<senha>@<cluster>.mongodb.net/recife_dados?retryWrites=true&w=majority
    ```
    _(Substitua <usuário>, <senha> e <cluster> pelas suas credenciais do MongoDB Atlas)_

3. Executar os processos ETL:
```bash
python -m etl.limpeza_urbana
python -m etl.obras_licenciamento
python -m etl.seguranca
python -m etl.educacao_saude
```

4. Iniciar o dashboard:
```bash
streamlit run dashboard.py
```

5. Acessar o dashboard:
    * Abra o navegador e acesse `http://localhost:8501`
    * Navegue pelas abas para visualizar as análises

## Estrutura de arquivos
```
pasta_do_projeto/
├── app.py
├── .env
├── database/
│   └── mongo_db.py
├── etl/
│   ├── limpeza_urbana.py
│   ├── obras_licenciamento.py
│   ├── seguranca.py
│   └── educacao_saude.py
└── data/
    └── raw/
        ├── licenciamento_ambiental.csv
        ├── licenciamento_urbanistico.csv
        ├── medicamentos.csv
        ├── roteirizacao.csv
        └── sedec2023.csv
```
