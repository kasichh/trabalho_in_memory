-- Consultas SQL para Indicadores do Sistema de Quiz

-- 1. Taxa de Acerto por Questão
-- Esta consulta calcula a porcentagem de acertos para cada questão
SELECT 
    q.question_id,
    q.question_text,
    a.nome AS assunto,
    d.nivel AS dificuldade,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_questao q
    JOIN dim_assunto a ON q.id_assunto = a.id
    JOIN dim_dificuldade d ON q.id_dificuldade = d.id
    LEFT JOIN fato_resposta r ON q.question_id = r.id_questao
GROUP BY 
    q.question_id, q.question_text, a.nome, d.nivel
ORDER BY 
    taxa_acerto DESC;

-- 2. Desempenho por Usuário
-- Esta consulta mostra o desempenho de cada usuário, incluindo total de respostas, acertos e taxa de acerto
SELECT 
    u.nome AS usuario,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_resposta r
    JOIN dim_usuario u ON r.id_usuario = u.id
GROUP BY 
    u.nome
ORDER BY 
    taxa_acerto DESC;

-- 3. Dificuldade Real das Questões vs. Dificuldade Cadastrada
-- Esta consulta compara a dificuldade cadastrada com a dificuldade real (baseada na taxa de acerto)
SELECT 
    q.question_id,
    q.question_text,
    d.nivel AS dificuldade_cadastrada,
    COUNT(r.id) AS total_respostas,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto,
    CASE 
        WHEN (SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100 < 40 THEN 'difícil'
        WHEN (SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100 < 70 THEN 'médio'
        ELSE 'fácil'
    END AS dificuldade_real
FROM 
    fato_questao q
    JOIN dim_dificuldade d ON q.id_dificuldade = d.id
    LEFT JOIN fato_resposta r ON q.question_id = r.id_questao
GROUP BY 
    q.question_id, q.question_text, d.nivel
HAVING 
    COUNT(r.id) > 0
ORDER BY 
    taxa_acerto;

-- 4. Distribuição de Respostas por Alternativa
-- Esta consulta mostra a distribuição das respostas por alternativa para cada questão
SELECT 
    q.question_id,
    q.question_text,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.alternativa_escolhida = 'a' THEN 1 ELSE 0 END) AS alternativa_a,
    SUM(CASE WHEN r.alternativa_escolhida = 'b' THEN 1 ELSE 0 END) AS alternativa_b,
    SUM(CASE WHEN r.alternativa_escolhida = 'c' THEN 1 ELSE 0 END) AS alternativa_c,
    SUM(CASE WHEN r.alternativa_escolhida = 'd' THEN 1 ELSE 0 END) AS alternativa_d,
    ROUND((SUM(CASE WHEN r.alternativa_escolhida = 'a' THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS pct_a,
    ROUND((SUM(CASE WHEN r.alternativa_escolhida = 'b' THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS pct_b,
    ROUND((SUM(CASE WHEN r.alternativa_escolhida = 'c' THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS pct_c,
    ROUND((SUM(CASE WHEN r.alternativa_escolhida = 'd' THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS pct_d,
    q.alternativa_correta
FROM 
    fato_questao q
    LEFT JOIN fato_resposta r ON q.question_id = r.id_questao
GROUP BY 
    q.question_id, q.question_text, q.alternativa_correta
HAVING 
    COUNT(r.id) > 0
ORDER BY 
    q.question_id;

-- 5. Progresso por Assunto
-- Esta consulta mostra o desempenho dos usuários por assunto
SELECT 
    a.nome AS assunto,
    u.nome AS usuario,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_resposta r
    JOIN fato_questao q ON r.id_questao = q.question_id
    JOIN dim_assunto a ON q.id_assunto = a.id
    JOIN dim_usuario u ON r.id_usuario = u.id
GROUP BY 
    a.nome, u.nome
ORDER BY 
    a.nome, taxa_acerto DESC;

-- 6. Evolução do Desempenho por Tentativa
-- Esta consulta mostra a evolução do desempenho dos usuários por tentativa
SELECT 
    u.nome AS usuario,
    r.nro_tentativa,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_resposta r
    JOIN dim_usuario u ON r.id_usuario = u.id
GROUP BY 
    u.nome, r.nro_tentativa
ORDER BY 
    u.nome, r.nro_tentativa;

-- 7. Ranking de Usuários por Desempenho
-- Esta consulta cria um ranking dos usuários com base na taxa de acerto
SELECT 
    u.nome AS usuario,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto,
    RANK() OVER (ORDER BY (SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) DESC) AS ranking
FROM 
    fato_resposta r
    JOIN dim_usuario u ON r.id_usuario = u.id
GROUP BY 
    u.nome
ORDER BY 
    ranking;

-- 8. Questões Mais Respondidas
-- Esta consulta mostra as questões mais respondidas
SELECT 
    q.question_id,
    q.question_text,
    a.nome AS assunto,
    d.nivel AS dificuldade,
    COUNT(r.id) AS total_respostas
FROM 
    fato_questao q
    JOIN dim_assunto a ON q.id_assunto = a.id
    JOIN dim_dificuldade d ON q.id_dificuldade = d.id
    LEFT JOIN fato_resposta r ON q.question_id = r.id_questao
GROUP BY 
    q.question_id, q.question_text, a.nome, d.nivel
ORDER BY 
    total_respostas DESC;

-- 9. Análise Temporal de Respostas
-- Esta consulta mostra a distribuição de respostas ao longo do tempo
SELECT 
    DATE_TRUNC('day', r.datahora) AS data,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_resposta r
GROUP BY 
    DATE_TRUNC('day', r.datahora)
ORDER BY 
    data;

-- 10. Análise de Desempenho por Dificuldade
-- Esta consulta mostra o desempenho dos usuários por nível de dificuldade
SELECT 
    d.nivel AS dificuldade,
    u.nome AS usuario,
    COUNT(r.id) AS total_respostas,
    SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) AS total_acertos,
    ROUND((SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(r.id)) * 100, 2) AS taxa_acerto
FROM 
    fato_resposta r
    JOIN fato_questao q ON r.id_questao = q.question_id
    JOIN dim_dificuldade d ON q.id_dificuldade = d.id
    JOIN dim_usuario u ON r.id_usuario = u.id
GROUP BY 
    d.nivel, u.nome
ORDER BY 
    d.nivel, taxa_acerto DESC;
