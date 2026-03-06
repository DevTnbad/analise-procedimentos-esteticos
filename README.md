# Dashboard de Análise de Procedimentos Estéticos

Projeto desenvolvido em Python com Streamlit para cadastrar clientes, procedimentos e atendimentos, além de gerar análises por faixa etária.

## Funcionalidades

- Primeiro acesso com criação de usuário
- Login com e-mail e senha
- Alteração de senha
- Cadastro de clientes
- Edição e exclusão de clientes
- Cadastro e exclusão de procedimentos
- Lançamento e exclusão de atendimentos
- Dashboard analítico com gráficos
- Filtros por procedimento e faixa etária
- Carga inicial com 30 clientes para testes

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- SQLite

## Estrutura do projeto

analise-procedimentos-esteticos/
├── app/
│   ├── auth.py
│   ├── database.py
│   └── dashboard.py
├── data/
├── requirements.txt
├── README.md
└── .gitignore

## Como executar

1. Criar ambiente virtual:
python -m venv .venv

2. Ativar ambiente virtual no Windows:
.venv\Scripts\activate

3. Instalar dependências:
pip install -r requirements.txt

4. Executar o sistema:
streamlit run app/dashboard.py