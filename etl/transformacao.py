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






    