
SELECT date_trunc('month', data_pedido)::date AS mes,
       count(*)                               AS pedidos,
       sum(valor_total)                       AS total_vendas
FROM pedidos
GROUP BY mes
ORDER BY mes;


SELECT (SELECT sum(total_vendas)
          FROM (SELECT sum(valor_total) AS total_vendas
                  FROM pedidos
                 GROUP BY date_trunc('month', data_pedido)) AS por_mes) AS soma_dos_meses,
       (SELECT sum(valor_total) FROM pedidos)                         AS soma_geral;


SELECT c.estado,
       count(*) AS pedidos
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY pedidos DESC;


SELECT id,
       valor_total,
       valor_itens,
       valor_total - valor_itens AS diferenca
FROM pedidos
WHERE divergente
ORDER BY id;