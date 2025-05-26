# Modelagem de Dados no Redis para o Sistema de Quiz

## Introdução

Este documento apresenta a modelagem de dados no Redis para o sistema de Quiz, conforme requisitos do trabalho final da disciplina In Memory DB. A modelagem foi baseada na análise do repositório de referência [apiQuestionRedis](https://github.com/commithouse/apiQuestionRedis) e adaptada para atender às necessidades específicas do projeto.

## Estruturas de Dados Utilizadas

O Redis oferece diferentes tipos de estruturas de dados que podem ser utilizadas de acordo com as necessidades da aplicação. Para o sistema de Quiz, utilizaremos principalmente **Hashes** (tabelas hash), que permitem armazenar campos e valores associados a uma chave.

### Entidades Principais

#### 1. Questões (Questions)

As questões são armazenadas como hashes no Redis, com a seguinte estrutura:

**Chave**: `question:{question_id}`

**Campos**:
- `question_text`: Texto da pergunta
- `alternativa_a`: Texto da alternativa A
- `alternativa_b`: Texto da alternativa B
- `alternativa_c`: Texto da alternativa C
- `alternativa_d`: Texto da alternativa D
- `alternativa_correta`: Alternativa correta (a, b, c ou d)
- `dificuldade`: Nível de dificuldade da questão (fácil, médio, difícil)
- `assunto`: Assunto ou categoria da questão

**Exemplo**:
```
HSET question:1 question_text "Qual é a resposta de tudo?" alternativa_a "1" alternativa_b "23" alternativa_c "42" alternativa_d "11" alternativa_correta "c" dificuldade "fácil" assunto "geek"
```

#### 2. Respostas (Answers)

As respostas dos usuários são armazenadas como hashes no Redis, com a seguinte estrutura:

**Chave**: `answer:{usuario}:{question_id}:{nro_tentativa}`

**Campos**:
- `question_id`: ID da questão respondida
- `alternativa_escolhida`: Alternativa escolhida pelo usuário (a, b, c ou d)
- `datahora`: Data e hora em que a resposta foi registrada
- `usuario`: Nome do usuário que respondeu
- `nro_tentativa`: Número da tentativa do usuário para esta questão

**Exemplo**:
```
HSET answer:dlemes:1:1 question_id 1 alternativa_escolhida "c" datahora "19/05/2025 09:47" usuario "dlemes" nro_tentativa 1
```

### Estruturas Auxiliares

#### 1. Índices para Consultas Rápidas

Para facilitar consultas específicas, podemos utilizar conjuntos (Sets) como índices:

**Questões por Assunto**:
- Chave: `index:assunto:{nome_do_assunto}`
- Valores: IDs das questões relacionadas ao assunto

**Exemplo**:
```
SADD index:assunto:geek 1 2
SADD index:assunto:tech 3
```

**Questões por Dificuldade**:
- Chave: `index:dificuldade:{nivel_dificuldade}`
- Valores: IDs das questões com o nível de dificuldade especificado

**Exemplo**:
```
SADD index:dificuldade:fácil 1 2 3
```

#### 2. Contadores

Para facilitar a geração de IDs únicos e estatísticas:

**Contador de Questões**:
- Chave: `counter:question`
- Valor: Número total de questões cadastradas

**Exemplo**:
```
INCR counter:question
```

**Contador de Respostas por Usuário**:
- Chave: `counter:answers:{usuario}`
- Valor: Número total de respostas do usuário

**Exemplo**:
```
INCR counter:answers:dlemes
```

## Justificativa das Escolhas

### 1. Uso de Hashes para Entidades Principais

Os hashes foram escolhidos para representar as entidades principais (questões e respostas) pelos seguintes motivos:

- **Eficiência de Armazenamento**: Hashes são mais eficientes em termos de memória quando comparados ao armazenamento de cada campo como uma chave separada.
- **Operações Atômicas**: Permitem operações atômicas em múltiplos campos de uma entidade.
- **Recuperação Parcial**: Possibilitam a recuperação de apenas alguns campos da entidade quando necessário, sem precisar carregar todos os dados.
- **Organização Lógica**: Mantêm os dados de uma entidade agrupados logicamente sob uma única chave.

### 2. Estrutura de Chaves

A estrutura de chaves foi projetada para:

- **Facilitar Buscas**: O formato `tipo:id` ou `tipo:usuario:id:tentativa` facilita a busca e recuperação de dados específicos.
- **Evitar Colisões**: A combinação de múltiplos identificadores nas chaves de respostas evita colisões e garante unicidade.
- **Suportar Padrões de Busca**: Permite o uso de padrões como `question:*` ou `answer:dlemes:*` para recuperar grupos de dados relacionados.

### 3. Índices Auxiliares

Os índices auxiliares (usando Sets) foram incluídos para:

- **Melhorar Performance de Consultas**: Permitem consultas rápidas por assunto ou dificuldade sem necessidade de varredura completa.
- **Facilitar Relatórios**: Simplificam a geração de relatórios e estatísticas por categoria.
- **Suportar Consultas Complexas**: Possibilitam operações de conjunto (união, interseção) para consultas mais complexas.

### 4. Contadores

Os contadores foram incluídos para:

- **Geração de IDs**: Facilitam a geração de IDs únicos e sequenciais para novas entidades.
- **Estatísticas em Tempo Real**: Permitem o acompanhamento em tempo real de métricas importantes.
- **Performance**: Operações de incremento são extremamente rápidas no Redis.

## Alinhamento com Requisitos dos Indicadores

A modelagem proposta suporta a geração dos seguintes indicadores:

1. **Taxa de Acerto por Questão**: Comparando as respostas dos usuários (`alternativa_escolhida`) com a resposta correta da questão (`alternativa_correta`).

2. **Desempenho por Usuário**: Analisando todas as respostas de um usuário específico através do padrão de chave `answer:{usuario}:*`.

3. **Dificuldade Real das Questões**: Calculando a taxa de acerto por questão e comparando com o nível de dificuldade cadastrado.

4. **Distribuição de Respostas por Alternativa**: Contando a frequência de cada alternativa escolhida para cada questão.

5. **Tempo Médio de Resposta**: Analisando os carimbos de data/hora das respostas consecutivas.

6. **Progresso por Assunto**: Agrupando o desempenho dos usuários por assunto das questões.

## Conclusão

A modelagem de dados proposta para o Redis foi projetada para atender aos requisitos do sistema de Quiz, garantindo eficiência no armazenamento e recuperação dos dados, além de suportar a geração dos indicadores necessários. A estrutura é flexível o suficiente para acomodar futuras expansões e otimizações conforme necessário.
