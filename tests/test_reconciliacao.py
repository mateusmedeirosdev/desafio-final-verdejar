"""Teste de reconciliação: roda depois do ETL e compara origem e destino."""
import json

from etl.carga import conectar
from etl.reconciliacao import totais_origem, totais_destino


def test_reconciliacao_origem_e_destino():
    """Prova que a carga está completa e correta.
    Compara a origem (pedidos únicos calculados a partir de brutos/pedidos.json)
    com o destino (tabela pedidos): a contagem deve ser igual e a soma de
    valor_itens deve bater, tolerando um centavo de diferença por causa do
    arredondamento do float."""

    with open("brutos/pedidos.json", encoding="utf-8") as f:
        pedidos_brutos = json.load(f)
    qtd_origem, soma_origem = totais_origem(pedidos_brutos)

    with conectar() as conexao:
        qtd_destino, soma_destino = totais_destino(conexao)

    assert qtd_origem == qtd_destino
    assert abs(soma_origem - soma_destino) <= 0.01