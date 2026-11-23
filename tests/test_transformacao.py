from etl.transformacao import tratar_email


def test_email_nulo_permanece_nulo():
    assert tratar_email(None) is None


def test_email_vazio_vira_nulo():
    assert tratar_email("") is None


def test_email_valido_permanece():
    assert tratar_email("diego@exemplo.com") == "diego@exemplo.com"