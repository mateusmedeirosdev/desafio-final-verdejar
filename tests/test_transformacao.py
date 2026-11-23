from etl.transformacao import tratar_email, padronizar_estado


def test_email_nulo_permanece_nulo():
    assert tratar_email(None) is None


def test_email_vazio_vira_nulo():
    assert tratar_email("") is None


def test_email_valido_permanece():
    assert tratar_email("diego@exemplo.com") == "diego@exemplo.com"

def test_estado_minusculo_vira_maiusculo():
    assert padronizar_estado("mg") == "MG"


def test_estado_maiusculo_permanece():
    assert padronizar_estado("SP") == "SP"


def test_estado_com_espacos_e_limpo():
    assert padronizar_estado(" rs ") == "RS"