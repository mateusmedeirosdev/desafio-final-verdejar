"""Funções de transformação das armadilhas A1 a A6.
Cada função recebe um valor e devolve o valor tratado,
sem acessar API, arquivo ou banco, para poder ser testada isoladamente.
"""
from datetime import datetime

def tratar_email(email):
    """ Armadilha - A1
    Trata o email, retornando None se for nulo ou vazio, caso contrário retorna o email.
    """
    if not email:
        return None
    else:
        return email

def padronizar_estado(estado):
    """ Armadilha - A2
    Padroniza o estado, removendo espaços e convertendo para maiúsculas.
    Estado nulo continua None; a coluna estado é NOT NULL e o banco recusa na carga.
    """
    if estado is None:
       return None
    return estado.strip().upper()

def converter_data(texto):
    """ Armadilha - A3
    Aceita os dois formatos que vêm da API: AAAA-MM-DD e DD/MM/AAAA.
    Devolve um objeto date, que o banco grava como DATE.
    Data inexistente (por exemplo, 31/02/2026) gera ValueError.

    Exemplos:
        converter_data("2026-02-19") -> date(2026, 2, 19)
        converter_data("19/02/2026") -> date(2026, 2, 19)
    """
    if "/" in texto:
        formato = "%d/%m/%Y"
    else:
        formato = "%Y-%m-%d"
    return datetime.strptime(texto, formato).date()

def converter_valor(valor):
    """ Armadilha - A4
    Converte o valor total do pedido para número com 2 casas (A4).

    O valor chega da API ora como número (94.34), ora como texto com
    vírgula decimal ("125,84"). Texto tem a vírgula trocada por ponto
    antes da conversão, porque float() só entende ponto como separador.
    
    Atenção: esta função NÃO trata separador de milhar ("1.234,56").
    Os dados da Verdejar não usam milhar, e remover os pontos antes da
    troca quebraria textos com ponto decimal:
    "94.34" -> "9434" -> 9434.0  (erro de 100 vezes)
    Esse caso é protegido pelo teste test_valor_texto_com_ponto_nao_e_multiplicado.

    Exemplos:
        converter_valor("125,84") -> 125.84
        converter_valor(94.34)    -> 94.34
        converter_valor("94.34")  -> 94.34

    """
    if isinstance(valor, str):
        valor = valor.replace(",", ".")
    return round(float(valor), 2)

def remover_repetidos(pedidos):
    """ Armadilha - A5
    Remove pedidos repetidos pelo campo "id", mantendo a primeira ocorrência.
    
    Devolve a lista de pedidos únicos e a quantidade de repetidos
    descartados. Usa um set para os ids vistos: a pergunta "já vi este id?"
    é instantânea, mesmo com milhares de pedidos.

    Exemplos:
    remover_repetidos([{"id": 1}, {"id": 2}, {"id": 1}])
        -> ([{"id": 1}, {"id": 2}], 1)

    remover_repetidos([{"id": 1, "pagina": "primeira"}, {"id": 1, "pagina": "segunda"}])
        -> ([{"id": 1, "pagina": "primeira"}], 1)

    remover_repetidos([{"id": 1}, {"id": 2}])
        -> ([{"id": 1}, {"id": 2}], 0)
    """
    id_vistos = set()
    pedidos_unicos = []
    for pedido in pedidos:
        if pedido["id"] in id_vistos:
            continue
        id_vistos.add(pedido["id"])
        pedidos_unicos.append(pedido)
    descartados = len(pedidos) - len(pedidos_unicos)
    return pedidos_unicos, descartados


def calcular_valor_itens(itens):
    """ Armadilha - A6
    Arredonda para centavos (2 casas). Sem isso, a soma pode sair com
    casas a mais, como 92.19999999999999 no lugar de 92.2, e a
    comparação com o valor_total ficaria errada.
    """
    total = 0
    for item in itens:
        total = total + item["quantidade"] * item["preco_unitario"]
    return round(total, 2)


def eh_divergente(valor_total, valor_itens):
    """ Armadilha - A6
    Indica se o valor total difere da soma dos itens em mais de 1 centavo (A6).
    A diferença é arredondada antes da comparação: 100.01 - 100.00 dá
    0.010000000000005116 no float, o que marcaria como divergente um
    pedido que está dentro da tolerância.
    """
    diferenca = round(abs(valor_total - valor_itens), 2)
    return diferenca > 0.01


def transformar_produtos(produtos_brutos):
    """Converte os tipos dos produtos lidos do CSV (todos chegam como texto)."""
    produtos = []
    for p in produtos_brutos:
        produtos.append({
            "produto_id": int(p["produto_id"]),
            "nome": p["nome"],
            "categoria": p["categoria"],
            "preco_base": round(float(p["preco_base"]), 2),
        })
    return produtos


def transformar_clientes(clientes_brutos):
    """Aplica A1 (e-mail nulo) e A2 (estado) em todos os clientes.

    Devolve a lista tratada e um dicionário de contadores.
    """
    clientes = []
    contadores = {"emails_nulos": 0, "estados_padronizados": 0}
    for c in clientes_brutos:
        email = tratar_email(c["email"])
        estado = padronizar_estado(c["estado"])
        if email is None:
            contadores["emails_nulos"] += 1
        if estado != c["estado"]:
            contadores["estados_padronizados"] += 1
        clientes.append({
            "id": c["id"],
            "nome": c["nome"],
            "email": email,
            "cidade": c["cidade"],
            "estado": estado,
            "cadastro_em": converter_data(c["cadastro_em"]),
        })
    return clientes, contadores


def transformar_pedidos(pedidos_brutos):
    """Aplica A5, A3, A4 e A6 nos pedidos e separa os itens.

    Os repetidos são removidos primeiro, para os contadores refletirem
    apenas os pedidos que vão para o banco. A API não envia o campo
    linha dos itens; ele é gerado pela posição do item no pedido (1, 2, 3...).

    Devolve (pedidos, itens, contadores).
    """
    unicos, repetidos = remover_repetidos(pedidos_brutos)
    pedidos = []
    itens = []
    contadores = {
        "pedidos_unicos": len(unicos),
        "repetidos_descartados": repetidos,
        "datas_convertidas": 0,
        "valores_convertidos": 0,
        "divergentes": 0,
    }
    for p in unicos:
        if "/" in p["data_pedido"]:
            contadores["datas_convertidas"] += 1
        if isinstance(p["valor_total"], str):
            contadores["valores_convertidos"] += 1

        valor_total = converter_valor(p["valor_total"])
        valor_itens = calcular_valor_itens(p["itens"])
        divergente = eh_divergente(valor_total, valor_itens)
        if divergente:
            contadores["divergentes"] += 1

        pedidos.append({
            "id": p["id"],
            "cliente_id": p["cliente_id"],
            "data_pedido": converter_data(p["data_pedido"]),
            "status": p["status"],
            "valor_total": valor_total,
            "valor_itens": valor_itens,
            "divergente": divergente,
        })
        for linha, item in enumerate(p["itens"], start=1):
            itens.append({
                "pedido_id": p["id"],
                "linha": linha,
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            })
    return pedidos, itens, contadores


    