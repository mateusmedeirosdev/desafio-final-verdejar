"""Reconciliação entre os dados brutos e o banco"""
from etl.transformacao import remover_repetidos, calcular_valor_itens


def totais_origem(pedidos_brutos):
    """Contagem de pedidos únicos e soma de valor_itens calculadas a partir dos brutos."""
    unicos, _ = remover_repetidos(pedidos_brutos)
    soma = sum(calcular_valor_itens(p["itens"]) for p in unicos)
    return len(unicos), round(soma, 2)


def totais_destino(conexao):
    """Contagem de pedidos e soma de valor_itens lidas da tabela pedidos."""
    with conexao.cursor() as cur:
        cur.execute("SELECT count(*), coalesce(sum(valor_itens), 0) FROM pedidos")
        quantidade, soma = cur.fetchone()
    return quantidade, round(float(soma), 2)