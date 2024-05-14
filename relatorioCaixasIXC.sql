-- Consulta movimentação financeira
-- Primeiro agrupa em termos do id_movim_finan a tabela de movimentação removendo as movimentações mestres.
WITH Credito AS (
    SELECT 
        fmf2.id_movim_finan idMovFina,
        fmf2.tipo_recebimento tpRec,
        SUM(valor_liquido_recebido) Entrada -- Soma entradas
    FROM 
        fn_movim_finan fmf2
    WHERE 
        fmf2.tipo_lanc IN ('R')
    GROUP BY
        fmf2.id_movim_finan, fmf2.tipo_recebimento
), 
Debito AS (
    SELECT 
        fmf2.id_movim_finan idMovFina,
        fmf2.tipo_recebimento tpRec,
        SUM(credito) Saida -- Soma entradas
    FROM 
        fn_movim_finan fmf2
    WHERE 
        fmf2.tipo_recebimento IN ('D', 'DP', 'CD', 'C', 'P', 'T')
        AND fmf2.tipo_lanc IN ('P', 'M')
    GROUP BY
        fmf2.id_movim_finan, fmf2.tipo_recebimento
),
Outros AS ( -- Entrada nos caixas
    SELECT 
        fmf2.id idMovFina,
        fmf2.tipo_recebimento tpRec,
        SUM(valor_liquido_recebido + debito) Entrada -- Soma entradas
    FROM 
        fn_movim_finan fmf2
    WHERE
        tipo_recebimento IN ('D', 'P')
        AND tipo_lanc = 'D'
    GROUP BY
        fmf2.id, fmf2.tipo_recebimento
),
tabelaGeral AS ( -- Foi feito o agrupamento pois se puxar a tabela 'crua' as 'entradas' estarão o valor no campo 'débito' e vice-versa
    SELECT 
        fmf.filial_id idFilial,
        fmf.id idContb,
        fmf.data Data,
        fmf.id_conta idPlanAnalitico,
        fmf.historico Historico,
        u.nome Operador,
        con.id idConta,
       IF( COALESCE(cred.tpRec, debt.tpRec, ou.tpRec) = 'DP', 'D', COALESCE(cred.tpRec, debt.tpRec, ou.tpRec)) tpRec,
        COALESCE(cred.Entrada, ou.Entrada, 0) Entrada,
        COALESCE(debt.Saida, 0) Saida
    FROM 
        fn_movim_finan AS fmf 
        LEFT JOIN Credito AS cred ON cred.idMovFina = fmf.id
        LEFT JOIN Debito AS debt ON debt.idMovFina = fmf.id
        LEFT JOIN usuarios AS u ON u.id = fmf.id_operador
        LEFT JOIN contas AS con ON con.id_planejamento = fmf.id_conta
        LEFT JOIN Outros AS ou ON ou.idMovFina = fmf.id
    WHERE 
        con.id = 214
        AND fmf.data <= '2024-05-14'
) -- SELECT * FROM tabelaGeral ORDER BY Data ASC;
SELECT
    Data,
    SUM(Entrada) Entrada, 
    SUM(Saida) Saida, 
    SUM(Entrada - Saida) Saldo,
    SUM(SUM(Entrada - Saida)) OVER (ORDER BY Data ASC) AS SaldoAcumulado
/* A operação acimaresponsável por calcular o saldo acumulado. O SUM(Entrada - Saida) calcula o saldo do dia, 
e a função de janela OVER (ORDER BY Data ASC) garante que o saldo acumulado seja calculado na ordem das datas.
*/
FROM 
    tabelaGeral
GROUP BY
    Data
ORDER BY 
    Data ASC;
