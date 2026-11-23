def tratar_email(email):
    """
    Trata o email, retornando None se for nulo ou vazio, caso contrário retorna o email.
    """
    if not email:
        return None
    else:
        return email

def padronizar_estado(estado):
    """
    Padroniza o estado, removendo espaços e convertendo para maiúsculas.
    """
    if estado is None:
        return None
    return estado.strip().upper()
