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




    