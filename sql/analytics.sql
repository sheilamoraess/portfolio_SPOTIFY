-- sql/analytics.sql
-- Consultas para descobrir os segredos das músicas usando o Banco de Dados

-- 1. DNA Sonoro dos Gêneros
-- Descobrindo qual gênero musical é mais dançante e mais enérgico
SELECT 
    f.genero,
    ROUND(AVG(a.danceability), 3) AS media_dancabilidade,
    ROUND(AVG(a.energy), 3) AS media_energia,
    COUNT(f.id) AS total_musicas
FROM faixas f
JOIN atributos_audio a ON f.id = a.faixa_id
WHERE f.genero IN ('sertanejo', 'funk', 'pop', 'hip-hop', 'rock') -- Filtrando gêneros famosos
GROUP BY f.genero
ORDER BY media_dancabilidade DESC;

-- 2. O Segredo do Hit (Músicas muito Populares vs Pouco Populares)
-- Agrupando as músicas por nível de popularidade para ver se Hits são mais animados
SELECT 
    CASE 
        WHEN f.popularidade >= 80 THEN '1. Mega Hit (Pop >= 80)'
        WHEN f.popularidade >= 50 THEN '2. Sucesso (Pop >= 50)'
        ELSE '3. Normal/Baixa (Pop < 50)'
    END AS categoria_popularidade,
    ROUND(AVG(a.danceability), 3) AS media_dancabilidade,
    ROUND(AVG(a.energy), 3) AS media_energia,
    ROUND(AVG(a.tempo), 1) AS bpm_medio,
    COUNT(f.id) AS total_musicas
FROM faixas f
JOIN atributos_audio a ON f.id = a.faixa_id
GROUP BY categoria_popularidade
ORDER BY categoria_popularidade ASC;
