from pii_scan_br.validators import cpf_valido, cnpj_valido, cnpj_numerico_valido, cnpj_alfanumerico_valido, mascarar
from tests.gerar import cpf, cnpj, cnpj_alfanumerico


def test_cpf_valido():
    v = cpf(1)
    assert cpf_valido(v)
    # DV alterado
    bad = v[:-1] + ("0" if v[-1] != "0" else "1")
    assert not cpf_valido(bad)


def test_cpf_rejeita_repetidos():
    assert not cpf_valido("111.111.111-11")
    assert not cpf_valido("000.000.000-00")


def test_cnpj_numerico():
    v = cnpj(2)
    assert cnpj_valido(v) and cnpj_numerico_valido(v)
    bad = v[:-1] + ("0" if v[-1] != "0" else "1")
    assert not cnpj_valido(bad)


def test_cnpj_alfanumerico():
    v = cnpj_alfanumerico(3)
    assert cnpj_valido(v) and cnpj_alfanumerico_valido(v)
    bad = v[:-1] + ("0" if v[-1] != "0" else "1")
    assert not cnpj_valido(bad)


def test_mascarar():
    v = cpf(1)
    m = mascarar("CPF", v)
    assert m == "***.***.**" + v[10] + "-" + v[12:14]
    assert v not in m
    assert "*" in m