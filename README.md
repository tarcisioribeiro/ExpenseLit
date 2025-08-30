# ExpenseLit - Frontend Streamlit

Sistema de controle financeiro pessoal desenvolvido em Streamlit, totalmente integrado com a [ExpenseLit API](../expenselit-api/).

## 🚀 Funcionalidades

### ✅ Implementadas
- **🔐 Sistema de Autenticação JWT** - Login seguro integrado com a API
- **🤖 Assistente IA Financeira** - GPT-4 + PostgreSQL 16.9 com pg_vector
  - Chat inteligente para consultas financeiras
  - Busca semântica por transações
  - Detecção automática de anomalias
  - Análise de padrões de gastos
  - Métricas avançadas com PostgreSQL analytics
- **🏦 Gestão de Contas** - CRUD completo de contas bancárias
- **💸 Gestão de Despesas** - Criação, edição e controle de despesas com filtros avançados
- **💰 Gestão de Receitas** - Registro e acompanhamento de receitas
- **💳 Cartões de Crédito** - Cadastro e gerenciamento de cartões
- **📊 Dashboard Interativo** - Visão geral com gráficos e métricas
- **👥 Membros** - Gestão de usuários e contatos
- **🤝 Empréstimos** - Sistema completo de empréstimos
- **🔄 Transferências** - Transferências entre contas
- **📈 Relatórios** - Análises e visualizações
- **🧭 Navegação Intuitiva** - Sidebar organizada por categorias
- **📱 Interface Responsiva** - Design otimizado para diferentes telas

## 📋 Pré-requisitos

### Dependências do Sistema
- Python 3.9+ 
- [ExpenseLit API](../expenselit-api/) rodando na porta 8002

### Dependências Python
Listadas no arquivo `requirements.txt`:
- streamlit>=1.28.0
- requests>=2.31.0 
- pandas>=2.0.0
- plotly>=5.15.0
- python-dotenv>=1.0.0
- pillow>=10.0.0

## 🛠️ Instalação

### 1. Clone e Navegue até o Diretório
```bash
cd ExpenseLit
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente
```bash
# Copie o template de configuração
cp .env.template .env

# Edite o arquivo .env com suas configurações
nano .env
```

### 4. Execute a Aplicação
```bash
streamlit run main.py
```

A aplicação estará disponível em: `http://localhost:8501`

## ⚙️ Configuração

### Arquivo .env
```env
# URL da API ExpenseLit
API_BASE_URL=http://localhost:8002

# PostgreSQL Database (para IA)
DB_HOSTNAME=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_NAME=financas

# OpenAI API Key (para IA Financeira)
OPENAI_API_KEY=sk-sua-chave-openai

# Debug (opcional)
DEBUG=true
```

### Configurações da API
Certifique-se de que a [ExpenseLit API](../expenselit-api/) está rodando e acessível na URL configurada.

## 🤖 IA Financeira - Recursos Avançados

### 🧠 Tecnologias Utilizadas
- **PostgreSQL 16.9** com extensão `pg_vector` para embeddings vetoriais
- **OpenAI GPT-4** para processamento de linguagem natural
- **text-embedding-3-small** para geração de embeddings semânticos
- **Índices HNSW** para busca vetorial ultra-rápida

### 🔥 Funcionalidades IA

#### 💬 Chat Inteligente
- Converse em linguagem natural sobre suas finanças
- O assistente entende contexto e consulta dados em tempo real
- Respostas personalizadas baseadas no seu perfil financeiro

#### 🔍 Busca Semântica
- Encontre transações por significado, não apenas palavras-chave
- Exemplo: "comida japonesa" encontra "sushi", "ramen", etc.
- Análise de similaridade vetorial com precisão avançada

#### 🚨 Detecção de Anomalias
- Identifica gastos anômalos automaticamente
- Análise estatística com Z-score e desvio padrão
- Alertas proativos sobre padrões suspeitos

#### 📊 Análise de Padrões
- Detecta tendências em categorias de gastos
- Análise de regressão linear para projeções
- Identificação de sazonalidades e ciclos

#### 📈 Métricas Avançadas
- Cálculos complexos usando PostgreSQL analytics
- Window functions para análises temporais
- Correlações entre diferentes tipos de transações

### 🛠️ Configuração Adicional para IA

#### 1. Instalar PostgreSQL 16.9
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-16 postgresql-contrib-16

# Instalar extensão pg_vector
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### 2. Configurar OpenAI API
1. Crie uma conta em [platform.openai.com](https://platform.openai.com)
2. Gere uma API key
3. Adicione ao arquivo `.env`

#### 3. Verificar Instalação IA
A aplicação verifica automaticamente:
- ✅ Conexão com PostgreSQL 16.9
- ✅ Extensão pg_vector habilitada  
- ✅ OpenAI API key válida

---

## 📜 Licença

Este projeto é licenciado sob a licença [MIT](LICENSE).

   A Licença MIT permite o uso, cópia, modificação e distribução do código do projeto, sem restrições. No entanto, a única exigência é que a licença original e o aviso de direitos autorais sejam mantidos, ou seja, deve-se deixar claro de onde o código veio.

 Sinta-se à vontade para usá-lo e modificá-lo conforme necessário.

## 📚 Referências

- [Documentação do Streamlit](https://docs.streamlit.io/)
- [MySQL Community Edition](https://dev.mysql.com/downloads/)
- [Python](https://www.python.org/)
