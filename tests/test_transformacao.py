from datetime import date

import pytest

from etl.transformacao import tratar_email, padronizar_estado, converter_data


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
    
def test_estado_nulo_permanece_nulo():
    assert padronizar_estado(None) is None

def test_data_formato_iso_vira_date():
    assert converter_data("2026-02-19") == date(2026, 2, 19)


def test_data_formato_brasileiro_vira_date():
    assert converter_data("19/02/2026") == date(2026, 2, 19)


def test_data_invalida_gera_erro():
    with pytest.raises(ValueError):
        converter_data("31/02/2026")