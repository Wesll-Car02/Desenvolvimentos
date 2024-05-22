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
),
resumoGeral AS (
    SELECT
        m.id idMov,
        m.data Data,
        m.debito AS Entrada,
        m.credito AS Saida,
        m.id_conta Conta,
        m.id_movim_finan idMov_M,
        COALESCE(r.tipo_recebimento, m.tipo_recebimento) AS tpRec
    FROM
        fn_movim_finan m
    LEFT JOIN
        Recebimentos r ON m.id_movim_finan = r.id_movim_finan
    WHERE 
        m.data >= '00-05-14' AND m.data <= '2024-04-30'
        AND m.id_conta = '913204'
    GROUP BY
        m.id,
        m.data,
        m.credito,
        m.debito,
        m.id_conta,
        m.id_movim_finan,
        COALESCE(r.tipo_recebimento, m.tipo_recebimento)
    ORDER BY
        m.id_movim_finan
)SELECT * FROM `resumoGeral`;
-- SELECT SUM(Entrada) AS Total_Entrada, SUM(Saida) AS Total_Saida FROM resumoGeral;
/*SELECT 
    Data,
    SUM(Entrada) Entrada, 
    SUM(Saida) Saida, 
    SUM(Entrada - Saida) Saldo,
    SUM(SUM(Entrada - Saida)) OVER (ORDER BY Data ASC) AS SaldoAcumulado
/* A operação acimaresponsável por calcular o saldo acumulado. O SUM(Entrada - Saida) calcula o saldo do dia, 
e a função de janela OVER (ORDER BY Data ASC) garante que o saldo acumulado seja calculado na ordem dAS datAS
FROM 
    resumoGeral
GROUP BY
    Data
ORDER BY 
    Data ASC
*/
