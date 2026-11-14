import os
import tempfile

from tests.gerar import cpf, cnpj, cnpj_alfanumerico
from pii_scan_br import scanner


def test_scan_detecta_cpf():
    v = cpf(5)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        with open(p, "w") as f:
            f.write(f"x {v} y\n")
        # scan file directly
        achados = scanner.scan_file(p, ignore_patterns=[], max_bytes=10**6, root=d)
        assert len(achados) == 1
        assert achados[0].tipo == "CPF"
        assert v not in achados[0].mascarado


def test_ignore_linha():
    v = cpf(6)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        with open(p, "w") as f:
            f.write(f"x {v} pii-scan-br: ignore\n")
        achados = scanner.scan_file(p, ignore_patterns=[], root=d)
        assert achados == []


def test_ignore_arquivo_glob():
    v = cpf(7)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "tests"))
        p = os.path.join(d, "tests", "f.txt")
        with open(p, "w") as f:
            f.write(v)
        ignore = os.path.join(d, ".pii-scan-br-ignore")
        with open(ignore, "w") as f:
            f.write("tests/**\n")
        old = os.getcwd()
        os.chdir(d)
        achados = scanner.scan_paths(["."], ignore_file=ignore, max_bytes=10**6)
        assert achados == []
        os.chdir(old)


def test_binario_e_tamanho():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "bin.bin")
        with open(p, "wb") as f:
            f.write(b"\x00" + b"123")
        assert scanner.scan_file(p, ignore_patterns=[], root=d) == []
        # arquivo grande
        p2 = os.path.join(d, "big.txt")
        with open(p2, "w") as f:
            f.write("a" * 100)
        assert scanner.scan_file(p2, ignore_patterns=[], max_bytes=10, root=d) == []


def test_saida_nao_contem_valor_completo():
    v = cpf(8)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        with open(p, "w") as f:
            f.write(v)
        old = os.getcwd()
        os.chdir(d)
        achados = scanner.scan_paths(["."], ignore_file="/dev/null", max_bytes=10**6)
        os.chdir(old)
        out = "\n".join(a.mascarado for a in achados)
        assert v not in out


def test_cnpj_alfanumerico_detectado():
    v = cnpj_alfanumerico(9)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        with open(p, "w") as f:
            f.write(v)
        achados = scanner.scan_file(p, ignore_patterns=[], root=d)
        assert len(achados) == 1
        assert achados[0].tipo == "CNPJ"