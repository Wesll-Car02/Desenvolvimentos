WITH Recebimentos AS (
    SELECT
        id_movim_finan,
        MAX(tipo_recebimento) AS tipo_recebimento
    FROM
        fn_movim_finan
    WHERE
        tipo_lanc != 'M'
    GROUP BY
        id_movim_finan
)
SELECT
    m.id,
    m.data,
    m.debito Entrada,
    m.credito Saida,
    m.id_movim_finan,
    m.tipo_lanc,
    COALESCE(r.tipo_recebimento, m.tipo_recebimento) AS tipo_recebimento_ajustado,
    SUM(m.valor_liquido_recebido) AS valor_liquido_recebido
FROM
    fn_movim_finan m
LEFT JOIN
    Recebimentos r ON m.id_movim_finan = r.id_movim_finan
WHERE 
    m.data >= '2024-05-14' AND m.data <= '2024-05-15'
    AND m.id_conta = '897727'
GROUP BY
    m.id,
    m.data,
    m.credito,
    m.debito,
    m.id_movim_finan,
    m.tipo_lanc,
    COALESCE(r.tipo_recebimento, m.tipo_recebimento)
ORDER BY
    m.id_movim_finan;
