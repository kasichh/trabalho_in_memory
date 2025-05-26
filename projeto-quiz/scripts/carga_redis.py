#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para carregar dados simulados no Redis para o sistema de Quiz.
Este script cria questões e respostas de exemplo no Redis, seguindo a modelagem definida.
"""

import redis
import json
import time
from datetime import datetime

# Configurações de conexão com o Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Dados simulados para questões
QUESTIONS = [
    {
        "question_id": 1,
        "question_text": "Qual é a principal vantagem do Redis como banco de dados em memória?",
        "alternativa_a": "Armazenamento em disco",
        "alternativa_b": "Alta velocidade de acesso",
        "alternativa_c": "Suporte nativo a SQL",
        "alternativa_d": "Baixo consumo de memória",
        "alternativa_correta": "b",
        "dificuldade": "fácil",
        "assunto": "banco de dados"
    },
    {
        "question_id": 2,
        "question_text": "Qual estrutura de dados do Redis é mais adequada para armazenar dados de sessão?",
        "alternativa_a": "Lists",
        "alternativa_b": "Sets",
        "alternativa_c": "Sorted Sets",
        "alternativa_d": "Hashes",
        "alternativa_correta": "d",
        "dificuldade": "médio",
        "assunto": "redis"
    },
    {
        "question_id": 3,
        "question_text": "Qual comando é usado para definir um tempo de expiração para uma chave no Redis?",
        "alternativa_a": "EXPIRE",
        "alternativa_b": "TTL",
        "alternativa_c": "TIMEOUT",
        "alternativa_d": "DEADLINE",
        "alternativa_correta": "a",
        "dificuldade": "fácil",
        "assunto": "redis"
    },
    {
        "question_id": 4,
        "question_text": "Qual é o principal uso do RedisGears?",
        "alternativa_a": "Processamento de imagens",
        "alternativa_b": "Execução de funções serverless",
        "alternativa_c": "Processamento de dados em tempo real",
        "alternativa_d": "Gerenciamento de filas",
        "alternativa_correta": "c",
        "dificuldade": "difícil",
        "assunto": "redis"
    },
    {
        "question_id": 5,
        "question_text": "Qual é a melhor estrutura de dados do Redis para implementar um ranking?",
        "alternativa_a": "Lists",
        "alternativa_b": "Sets",
        "alternativa_c": "Hashes",
        "alternativa_d": "Sorted Sets",
        "alternativa_correta": "d",
        "dificuldade": "médio",
        "assunto": "redis"
    }
]

# Dados simulados para respostas
ANSWERS = [
    {
        "question_id": 1,
        "alternativa_escolhida": "b",
        "datahora": "22/05/2025 10:15",
        "usuario": "maria",
        "nro_tentativa": 1
    },
    {
        "question_id": 1,
        "alternativa_escolhida": "a",
        "datahora": "22/05/2025 10:20",
        "usuario": "joao",
        "nro_tentativa": 1
    },
    {
        "question_id": 2,
        "alternativa_escolhida": "d",
        "datahora": "22/05/2025 10:25",
        "usuario": "maria",
        "nro_tentativa": 1
    },
    {
        "question_id": 2,
        "alternativa_escolhida": "b",
        "datahora": "22/05/2025 10:30",
        "usuario": "joao",
        "nro_tentativa": 1
    },
    {
        "question_id": 3,
        "alternativa_escolhida": "a",
        "datahora": "22/05/2025 10:35",
        "usuario": "maria",
        "nro_tentativa": 1
    },
    {
        "question_id": 3,
        "alternativa_escolhida": "b",
        "datahora": "22/05/2025 10:40",
        "usuario": "joao",
        "nro_tentativa": 1
    },
    {
        "question_id": 4,
        "alternativa_escolhida": "d",
        "datahora": "22/05/2025 10:45",
        "usuario": "maria",
        "nro_tentativa": 1
    },
    {
        "question_id": 4,
        "alternativa_escolhida": "c",
        "datahora": "22/05/2025 10:50",
        "usuario": "joao",
        "nro_tentativa": 1
    },
    {
        "question_id": 5,
        "alternativa_escolhida": "d",
        "datahora": "22/05/2025 10:55",
        "usuario": "maria",
        "nro_tentativa": 1
    },
    {
        "question_id": 5,
        "alternativa_escolhida": "a",
        "datahora": "22/05/2025 11:00",
        "usuario": "joao",
        "nro_tentativa": 1
    },
    # Segunda tentativa para algumas questões
    {
        "question_id": 1,
        "alternativa_escolhida": "b",
        "datahora": "22/05/2025 11:05",
        "usuario": "joao",
        "nro_tentativa": 2
    },
    {
        "question_id": 3,
        "alternativa_escolhida": "a",
        "datahora": "22/05/2025 11:10",
        "usuario": "joao",
        "nro_tentativa": 2
    },
    {
        "question_id": 4,
        "alternativa_escolhida": "c",
        "datahora": "22/05/2025 11:15",
        "usuario": "maria",
        "nro_tentativa": 2
    }
]

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

def clear_existing_data(r):
    """Limpa dados existentes no Redis."""
    # Remove todas as chaves de questões
    question_keys = r.keys("question:*")
    if question_keys:
        r.delete(*question_keys)
        print(f"Removidas {len(question_keys)} questões existentes.")
    
    # Remove todas as chaves de respostas
    answer_keys = r.keys("answer:*")
    if answer_keys:
        r.delete(*answer_keys)
        print(f"Removidas {len(answer_keys)} respostas existentes.")
    
    # Remove índices
    index_keys = r.keys("index:*")
    if index_keys:
        r.delete(*index_keys)
        print(f"Removidos {len(index_keys)} índices existentes.")
    
    # Remove contadores
    counter_keys = r.keys("counter:*")
    if counter_keys:
        r.delete(*counter_keys)
        print(f"Removidos {len(counter_keys)} contadores existentes.")

def load_questions(r, questions):
    """Carrega questões no Redis."""
    for question in questions:
        # Cria a chave da questão
        question_key = f"question:{question['question_id']}"
        
        # Armazena a questão como um hash
        r.hset(
            question_key,
            mapping={
                'question_text': question['question_text'],
                'alternativa_a': question['alternativa_a'],
                'alternativa_b': question['alternativa_b'],
                'alternativa_c': question['alternativa_c'],
                'alternativa_d': question['alternativa_d'],
                'alternativa_correta': question['alternativa_correta'],
                'dificuldade': question['dificuldade'],
                'assunto': question['assunto']
            }
        )
        
        # Atualiza índices
        r.sadd(f"index:assunto:{question['assunto']}", question['question_id'])
        r.sadd(f"index:dificuldade:{question['dificuldade']}", question['question_id'])
        
        # Atualiza contador
        r.set(f"counter:question", max(int(r.get(f"counter:question") or 0), question['question_id']))
        
        print(f"Questão {question['question_id']} carregada com sucesso.")

def load_answers(r, answers):
    """Carrega respostas no Redis."""
    for answer in answers:
        # Cria a chave da resposta
        answer_key = f"answer:{answer['usuario']}:{answer['question_id']}:{answer['nro_tentativa']}"
        
        # Armazena a resposta como um hash
        r.hset(
            answer_key,
            mapping={
                'question_id': answer['question_id'],
                'alternativa_escolhida': answer['alternativa_escolhida'],
                'datahora': answer['datahora'],
                'usuario': answer['usuario'],
                'nro_tentativa': answer['nro_tentativa']
            }
        )
        
        # Atualiza contador de respostas por usuário
        r.incr(f"counter:answers:{answer['usuario']}")
        
        print(f"Resposta do usuário {answer['usuario']} para questão {answer['question_id']} (tentativa {answer['nro_tentativa']}) carregada com sucesso.")

def save_data_to_json():
    """Salva os dados simulados em arquivos JSON."""
    with open('/home/ubuntu/projeto-quiz/redis/questions.json', 'w', encoding='utf-8') as f:
        json.dump(QUESTIONS, f, ensure_ascii=False, indent=2)
    
    with open('/home/ubuntu/projeto-quiz/redis/answers.json', 'w', encoding='utf-8') as f:
        json.dump(ANSWERS, f, ensure_ascii=False, indent=2)
    
    print("Dados salvos em arquivos JSON.")

def main():
    """Função principal."""
    print("Iniciando carga de dados no Redis...")
    
    # Salva os dados em arquivos JSON
    save_data_to_json()
    
    # Conecta ao Redis
    r = connect_to_redis()
    if not r:
        return
    
    # Limpa dados existentes
    clear_existing_data(r)
    
    # Carrega questões
    print("\nCarregando questões...")
    load_questions(r, QUESTIONS)
    
    # Carrega respostas
    print("\nCarregando respostas...")
    load_answers(r, ANSWERS)
    
    # Verifica a carga
    total_questions = len(r.keys("question:*"))
    total_answers = len(r.keys("answer:*"))
    
    print("\nCarga concluída com sucesso!")
    print(f"Total de questões carregadas: {total_questions}")
    print(f"Total de respostas carregadas: {total_answers}")

if __name__ == "__main__":
    main()
