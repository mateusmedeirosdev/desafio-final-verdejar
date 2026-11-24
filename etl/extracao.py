
import csv
import json
import os
import sys

import requests

URL_BASE = "http://127.0.0.1:8000"
PASTA_BRUTOS = "brutos"

def extrair_paginado(rota, page_size=200):
    """Percorre todas as paginas de uma rota da API e devolve (lista_de_itens, numero_de_paginas).
    Em caso aconteça algum erro, retorna uma mensagem avisando do erro e encerra o programa.
    """
    itens = []
    pagina = 1
    total_paginas = 1

    while pagina <= total_paginas:
        url = f"{URL_BASE}/{rota}"
        parametros = {"page": pagina, "page_size": page_size}

        try:
            resposta = requests.get(url, params=parametros, timeout=10)
        except requests.exceptions.ConnectionError:
            print(f"erro: nao foi possivel conectar em {URL_BASE}. A API esta rodando?")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print(f"erro: a API nao respondeu em 10 segundos (rota={rota} pagina={pagina})")
            sys.exit(1)

        if resposta.status_code != 200:
            print(f"erro: rota={rota} pagina={pagina} status={resposta.status_code}")
            sys.exit(1)

        dados = resposta.json()
        itens.extend(dados["items"])
        total_paginas = dados["total_pages"]
        pagina += 1

    return itens, total_paginas

def ler_produtos_csv(caminho):
    """Le o CSV de produtos, todos os valores vao chegar como texto."""
    try:
        with open(caminho, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"erro: arquivo nao encontrado: {caminho}")
        sys.exit(1)


def salvar_bruto(nome, dados):
    """Grava os dados sem nenhuma alteracao em brutos/<nome>.json."""
    os.makedirs(PASTA_BRUTOS, exist_ok=True)
    caminho = os.path.join(PASTA_BRUTOS, f"{nome}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    clientes, pags_clientes = extrair_paginado("clientes")
    print(f"extracao: clientes paginas={pags_clientes} registros={len(clientes)}")
    salvar_bruto("clientes", clientes)

    pedidos, pags_pedidos = extrair_paginado("pedidos")
    print(f"extracao: pedidos paginas={pags_pedidos} registros_brutos={len(pedidos)}")
    salvar_bruto("pedidos", pedidos)

    produtos = ler_produtos_csv("insumos/dados/produtos.csv")
    print(f"extracao: produtos registros={len(produtos)}")
    salvar_bruto("produtos", produtos)

    