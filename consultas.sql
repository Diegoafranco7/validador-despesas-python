-- Consultas reais do banco gerado em saida/despesas.sqlite3.
-- Todos os totais usam centavos inteiros; somente registros válidos entram na soma.
SELECT situacao, COUNT(*) AS quantidade FROM despesas GROUP BY situacao;

SELECT categoria, COUNT(*) AS quantidade, SUM(valor_centavos) AS total_centavos
FROM despesas WHERE situacao = 'valido'
GROUP BY categoria ORDER BY total_centavos DESC;

SELECT linha, id, fornecedor, valor, motivos
FROM despesas WHERE situacao = 'pendente' ORDER BY linha;

SELECT id, COUNT(*) AS ocorrencias FROM despesas
WHERE id <> '' GROUP BY id HAVING COUNT(*) > 1;

SELECT d.linha, d.categoria AS categoria_original, s.categoria_sugerida,
       s.justificativa, s.origem
FROM sugestoes_ia AS s JOIN despesas AS d ON d.linha = s.linha;
