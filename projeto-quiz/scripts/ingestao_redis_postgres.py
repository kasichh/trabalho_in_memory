#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ingestão de dados do Redis para o PostgreSQL.
Este script transfere questões e respostas do Redis para o PostgreSQL,
seguindo a modelagem definida para o sistema de Quiz.
"""

import redis
import psycopg2
import time
import json
from datetime import datetime

# Configurações de conexão com o Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Configurações de conexão com o PostgreSQL
PG_HOST = 'localhost'
PG_PORT = 5432
PG_DB = 'quiz_dw'
PG_USER = 'ubuntu'
PG_PASSWORD = 'senha123'

# Intervalo de verificação (em segundos)
CHECK_INTERVAL = 5

def connect_to_redis():
    """Estabelece conexão com o Redis."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()  # Verifica se a conexão está ativa
        print("Conexão com o Redis estabelecida com sucesso!")
        return r
    except redis.ConnectionError:
        print("Erro ao conectar ao Redis. Verifique se o servidor está em execução.")
        return None

def connect_to_postgres():
    """Estabelece conexão com o PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print("Conexão com o PostgreSQL estabelecida com sucesso!")
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def create_tables(conn):
    """Cria as tabelas necessárias no PostgreSQL se não existirem."""
    with conn.cursor() as cur:
        # Tabela de dimensão para assuntos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_assunto (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        # Tabela de dimensão para níveis de dificuldade
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_dificuldade (
                id SERIAL PRIMARY KEY,
                nivel VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        
        # Tabela de dimensão para usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_usuario (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        # Tabela de fato para questões
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fato_questao (
                id SERIAL PRIMARY KEY,
                question_id INTEGER UNIQUE NOT NULL,
                question_text TEXT NOT NULL,
                alternativa_a TEXT NOT NULL,
                alternativa_b TEXT NOT NULL,
                alternativa_c TEXT NOT NULL,
                alternativa_d TEXT NOT NULL,
                alternativa_correta CHAR(1) NOT NULL,
                id_dificuldade INTEGER REFERENCES dim_dificuldade(id),
                id_assunto INTEGER REFERENCES dim_assunto(id),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabela de fato para respostas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fato_resposta (
                id SERIAL PRIMARY KEY,
                id_questao INTEGER REFERENCES fato_questao(question_id),
                id_usuario INTEGER REFERENCES dim_usuario(id),
                alternativa_escolhida CHAR(1) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                nro_tentativa INTEGER NOT NULL,
                datahora TIMESTAMP NOT NULL,
                data_ingestao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id_questao, id_usuario, nro_tentativa)
            );
        """)
        
        # Tabela de log para rastreamento de ingestão
        cur.execute("""
            CREATE TABLE IF NOT EXISTS log_ingestao (
                id SERIAL PRIMARY KEY,
                entidade VARCHAR(50) NOT NULL,
                chave_redis VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                mensagem TEXT,
                data_ingestao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
    conn.commit()
    print("Tabelas criadas/verificadas com sucesso!")

def get_or_create_dimension(conn, table, column, value):
    """Obtém ou cria um registro em uma tabela de dimensão."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
        result = cur.fetchone()
        
        if result:
            return result[0]
        else:
            cur.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
            return cur.fetchone()[0]

def process_questions(r, conn):
    """Processa questões do Redis e insere no PostgreSQL."""
    question_keys = r.keys("question:*")
    processed_count = 0
    
    for key in question_keys:
        question = r.hgetall(key)
        if not question:
            continue
        
        question_id = int(key.split(':')[1])
        
        try:
            # Verifica se a questão já existe no PostgreSQL
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM fato_questao WHERE question_id = %s", (question_id,))
                if cur.fetchone():
                    # Registra no log que a questão já existe
                    cur.execute(
                        "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                        ("questao", key, "ignorado", "Questão já existe no banco de dados")
                    )
                    continue
            
            # Obtém ou cria registros nas tabelas de dimensão
            id_dificuldade = get_or_create_dimension(conn, "dim_dificuldade", "nivel", question.get('dificuldade', 'desconhecido'))
            id_assunto = get_or_create_dimension(conn, "dim_assunto", "nome", question.get('assunto', 'geral'))
            
            # Insere a questão na tabela de fato
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO fato_questao 
                    (question_id, question_text, alternativa_a, alternativa_b, alternativa_c, alternativa_d, 
                     alternativa_correta, id_dificuldade, id_assunto)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    question_id,
                    question.get('question_text', ''),
                    question.get('alternativa_a', ''),
                    question.get('alternativa_b', ''),
                    question.get('alternativa_c', ''),
                    question.get('alternativa_d', ''),
                    question.get('alternativa_correta', ''),
                    id_dificuldade,
                    id_assunto
                ))
                
                # Registra no log o sucesso da ingestão
                cur.execute(
                    "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                    ("questao", key, "sucesso", "Questão inserida com sucesso")
                )
                
                processed_count += 1
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            # Registra no log o erro na ingestão
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                    ("questao", key, "erro", str(e))
                )
            print(f"Erro ao processar questão {key}: {e}")
    
    return processed_count

def process_answers(r, conn):
    """Processa respostas do Redis e insere no PostgreSQL."""
    answer_keys = r.keys("answer:*")
    processed_count = 0
    
    for key in answer_keys:
        answer = r.hgetall(key)
        if not answer:
            continue
        
        parts = key.split(':')
        if len(parts) < 4:
            continue
        
        usuario = parts[1]
        question_id = int(parts[2])
        nro_tentativa = int(parts[3])
        
        try:
            # Verifica se a resposta já existe no PostgreSQL
            with conn.cursor() as cur:
                # Obtém o ID do usuário (cria se não existir)
                id_usuario = get_or_create_dimension(conn, "dim_usuario", "nome", usuario)
                
                # Verifica se a resposta já existe
                cur.execute(
                    "SELECT 1 FROM fato_resposta WHERE id_questao = %s AND id_usuario = %s AND nro_tentativa = %s",
                    (question_id, id_usuario, nro_tentativa)
                )
                if cur.fetchone():
                    # Registra no log que a resposta já existe
                    cur.execute(
                        "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                        ("resposta", key, "ignorado", "Resposta já existe no banco de dados")
                    )
                    continue
                
                # Verifica se a questão existe no PostgreSQL
                cur.execute("SELECT alternativa_correta FROM fato_questao WHERE question_id = %s", (question_id,))
                question_result = cur.fetchone()
                if not question_result:
                    # Registra no log que a questão não existe
                    cur.execute(
                        "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                        ("resposta", key, "pendente", "Questão relacionada não encontrada no banco de dados")
                    )
                    continue
                
                alternativa_correta = question_result[0]
                alternativa_escolhida = answer.get('alternativa_escolhida', '')
                is_correct = (alternativa_escolhida == alternativa_correta)
                
                # Converte a string de data/hora para timestamp
                datahora_str = answer.get('datahora', '')
                try:
                    datahora = datetime.strptime(datahora_str, "%d/%m/%Y %H:%M")
                except ValueError:
                    datahora = datetime.now()
                
                # Insere a resposta na tabela de fato
                cur.execute("""
                    INSERT INTO fato_resposta 
                    (id_questao, id_usuario, alternativa_escolhida, is_correct, nro_tentativa, datahora)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    question_id,
                    id_usuario,
                    alternativa_escolhida,
                    is_correct,
                    nro_tentativa,
                    datahora
                ))
                
                # Registra no log o sucesso da ingestão
                cur.execute(
                    "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                    ("resposta", key, "sucesso", "Resposta inserida com sucesso")
                )
                
                processed_count += 1
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            # Registra no log o erro na ingestão
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO log_ingestao (entidade, chave_redis, status, mensagem) VALUES (%s, %s, %s, %s)",
                    ("resposta", key, "erro", str(e))
                )
            print(f"Erro ao processar resposta {key}: {e}")
    
    return processed_count

def main():
    """Função principal."""
    print("Iniciando processo de ingestão Redis → PostgreSQL...")
    
    # Conecta ao Redis
    r = connect_to_redis()
    if not r:
        return
    
    # Conecta ao PostgreSQL
    conn = connect_to_postgres()
    if not conn:
        return
    
    # Cria as tabelas necessárias
    create_tables(conn)
    
    # Executa uma vez imediatamente
    print("\nProcessando questões...")
    questions_processed = process_questions(r, conn)
    print(f"Processadas {questions_processed} questões.")
    
    print("\nProcessando respostas...")
    answers_processed = process_answers(r, conn)
    print(f"Processadas {answers_processed} respostas.")
    
    print("\nIngestão inicial concluída!")
    
    # Loop contínuo para verificar novas entradas
    print("\nIniciando monitoramento contínuo...")
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Verificando novas entradas...")
            
            questions_processed = process_questions(r, conn)
            if questions_processed > 0:
                print(f"Processadas {questions_processed} novas questões.")
            
            answers_processed = process_answers(r, conn)
            if answers_processed > 0:
                print(f"Processadas {answers_processed} novas respostas.")
            
            if questions_processed == 0 and answers_processed == 0:
                print("Nenhuma nova entrada encontrada.")
            
            print(f"Aguardando {CHECK_INTERVAL} segundos...")
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nProcesso de ingestão interrompido pelo usuário.")
    finally:
        if conn:
            conn.close()
        print("Conexões fechadas. Processo finalizado.")

if __name__ == "__main__":
    main()
