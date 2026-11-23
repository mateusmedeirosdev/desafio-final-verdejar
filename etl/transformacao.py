"""Funções de transformação das armadilhas A1 a A6.
Cada função recebe um valor e devolve o valor tratado,
sem acessar API, arquivo ou banco, para poder ser testada isoladamente.
"""

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
    """
    if estado is None:
       return None
    return estado.strip().upper()
