"""Validadores de CPF e CNPJ (numérico e alfanumérico) com dígito verificador."""

import re


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def cpf_valido(value: str) -> bool:
    d = [int(c) for c in _digits(value)]
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for size in (9, 10):
        total = sum(d[i] * (size + 1 - i) for i in range(size))
        if (total * 10) % 11 % 10 != d[size]:
            return False
    return True


def cnpj_numerico_valido(value: str) -> bool:
    d = [int(c) for c in _digits(value)]
    if len(d) != 14 or len(set(d)) == 1:
        return False
    for size in (12, 13):
        weights = list(range(size - 7, 1, -1)) + list(range(9, 1, -1))
        total = sum(d[i] * weights[i] for i in range(size))
        rest = total % 11
        dv = 0 if rest < 2 else 11 - rest
        if dv != d[size]:
            return False
    return True


def cnpj_alfanumerico_valido(value: str) -> bool:
    raw = re.sub(r"[./\s-]", "", value or "").upper()
    if len(raw) != 14 or not raw.isascii() or not raw.isalnum():
        return False
    if raw.isdigit():
        return False  # caso numérico, tratado por cnpj_numerico_valido
    if not raw[:12].isalnum() or not raw[12:].isdigit():
        return False
    if not all(c.isdigit() or ("A" <= c <= "Z") for c in raw[:12]):
        return False
    d = [ord(c) - 48 for c in raw]
    for size in (12, 13):
        weights = list(range(size - 7, 1, -1)) + list(range(9, 1, -1))
        rest = sum(d[i] * weights[i] for i in range(size)) % 11
        dv = 0 if rest < 2 else 11 - rest
        if dv != d[size]:
            return False
    return True


def cnpj_valido(value: str) -> bool:
    return cnpj_numerico_valido(value) or cnpj_alfanumerico_valido(value)


def mascarar(tipo: str, valor: str) -> str:
    if tipo == "CPF":
        d = _digits(valor)
        if len(d) != 11:
            return valor
        m = "*" * 8 + d[8:]
        return f"{m[0:3]}.{m[3:6]}.{m[6:9]}-{m[9:11]}"
    raw = re.sub(r"[./\s-]", "", valor or "").upper()
    if len(raw) != 14:
        return valor
    m = "*" * 11 + raw[11:]
    return f"{m[0:2]}.{m[2:5]}.{m[5:8]}/{m[8:12]}-{m[12:14]}"