# Projeto de Ingestão e Armazenamento de Dados do QUIZ com Redis e Data Warehouse


Estou compartilhando o projeto completo desenvolvido para o trabalho final da disciplina In Memory DB. 
Este projeto implementa um sistema de ingestão de dados para um Quiz, utilizando Redis como banco intermediário 
e PostgreSQL como Data Warehouse, com foco na estruturação dos dados e geração de indicadores.

## O que está incluído no pacote

O arquivo zip contém todos os componentes necessários para entender, executar e apresentar o projeto:

1. **Documentação Completa** (`/docs`)
   - `documentacao.pdf`: Documento principal explicando todo o projeto
   - `modelo_dados_redis.md`: Detalhamento da modelagem no Redis
   - `arquitetura.png`: Diagrama da arquitetura do sistema

2. **Scripts de Implementação** (`/scripts`)
   - `carga_redis.py`: Script para popular o Redis com dados simulados
   - `ingestao_redis_postgres.py`: Mecanismo de ingestão do Redis para o PostgreSQL

3. **Dados de Exemplo** (`/redis`)
   - `questions.json`: Exemplos de questões para o Quiz
   - `answers.json`: Exemplos de respostas dos usuários

4. **Consultas SQL** (`/postgres`)
   - `consultas_indicadores.sql`: Consultas para gerar indicadores e relatórios

## Entregáveis do Trabalho

Todos os entregáveis solicitados foram desenvolvidos:

1. **Definição das Estruturas de Dados no Redis**
   - Modelagem das entidades do Quiz (questões, respostas)
   - Justificativa das escolhas com base nos requisitos

2. **Exemplos de Carga de Dados**
   - Scripts para popular o Redis com dados simulados

3. **Mecanismo de Ingestão**
   - Implementação da ingestão de dados do Redis para o PostgreSQL
   - Fluxos de ingestão de perguntas e respostas funcionando

4. **Modelagem no DW e Consultas**
   - Tabelas no PostgreSQL com os dados carregados
   - Consultas SQL que geram os indicadores solicitados

5. **Documentação**
   - PDF explicativo do projeto completo

## Como executar o projeto

Para executar o projeto em seu ambiente local:

1. **Configurar o Redis**
   ```
   sudo apt-get install redis-server
   sudo systemctl start redis-server
   ```

2. **Configurar o PostgreSQL**
   ```
   sudo apt-get install postgresql
   sudo -u postgres psql -c "CREATE USER seu_usuario WITH SUPERUSER PASSWORD 'senha123';"
   sudo -u postgres psql -c "CREATE DATABASE quiz_dw OWNER seu_usuario;"
   ```

3. **Instalar dependências Python**
   ```
   pip install redis psycopg2-binary
   ```

4. **Executar o script de carga**
   ```
   python scripts/carga_redis.py
   ```

5. **Executar o mecanismo de ingestão**
   ```
   python scripts/ingestao_redis_postgres.py
   ```

6. **Executar as consultas SQL**
   As consultas podem ser executadas diretamente no PostgreSQL para visualizar os indicadores.

## Próximos passos

Para finalizar a entrega do trabalho, precisamos:

1. Criar Documentação no Github.
2. Gravar um vídeo curto explicando a solução implementada.
3. Compartilhar o vídeo com o professor conforme as instruções

Sugiro que revisemos juntos o material antes da gravação do vídeo para garantir que todos estejam 
alinhados com a solução desenvolvida.
