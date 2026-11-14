"""Gera CPF/CNPJ sintéticos válidos (semente fixa)."""

import random


def _cpf_dvs(base):
    d = list(base)
    for size in (9, 10):
        total = sum(d[i] * (size + 1 - i) for i in range(size))
        d.append((total * 10) % 11 % 10)
    return d


def cpf(semente=42, formatado=True):
    rng = random.Random(semente)
    while True:
        base = [rng.randint(0, 9) for _ in range(9)]
        if all(x == base[0] for x in base):
            continue
        d = _cpf_dvs(base)
        if all(x == d[0] for x in d):
            continue
        break
    s = "".join(map(str, d))
    if formatado:
        return f"{s[0:3]}.{s[3:6]}.{s[6:9]}-{s[9:11]}"
    return s


def cnpj(semente=42, formatado=True):
    rng = random.Random(semente)
    while True:
        base = [rng.randint(0, 9) for _ in range(12)]
        d = list(base)
        for size in (12, 13):
            weights = list(range(size - 7, 1, -1)) + list(range(9, 1, -1))
            total = sum(d[i] * weights[i] for i in range(size))
            rest = total % 11
            d.append(0 if rest < 2 else 11 - rest)
        if all(x == d[0] for x in d):
            continue
        break
    s = "".join(map(str, d))
    if formatado:
        return f"{s[0:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:14]}"
    return s


def cnpj_alfanumerico(semente=42, formatado=True):
    rng = random.Random(semente + 1)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while True:
        base = [rng.choice(alphabet) for _ in range(12)]
        if all(c.isdigit() for c in base):
            base[0] = "A"
        dvals = [ord(c) - 48 for c in base]
        d = list(dvals)
        for size in (12, 13):
            weights = list(range(size - 7, 1, -1)) + list(range(9, 1, -1))
            total = sum(d[i] * weights[i] for i in range(size))
            rest = total % 11
            dv = 0 if rest < 2 else 11 - rest
            d.append(dv)
        raw = "".join(base) + str(d[12]) + str(d[13])
        if all(c == raw[0] for c in raw):
            continue
        break
    if formatado:
        return f"{raw[0:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:14]}"
    return raw