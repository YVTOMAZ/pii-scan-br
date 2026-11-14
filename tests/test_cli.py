import json
import os
import subprocess
import tempfile

from tests.gerar import cpf
from pii_scan_br.cli import main


def test_exit_codes():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        with open(p, "w") as f:
            f.write("nada aqui")
        assert main([p]) == 0
        v = cpf(10)
        with open(p, "w") as f:
            f.write(v)
        assert main([p]) == 1


def test_format_json():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.txt")
        v = cpf(11)
        with open(p, "w") as f:
            f.write(v)
        # capture stdout
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main([p, "--format", "json"])
        assert code == 1
        data = json.loads(buf.getvalue())
        assert isinstance(data, list) and data
        assert "masked" in data[0]


def test_diff():
    with tempfile.TemporaryDirectory() as d:
        old = os.getcwd()
        os.chdir(d)
        subprocess.run(["git", "init", "-q"], check=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], check=True)
        subprocess.run(["git", "config", "user.name", "t"], check=True)
        base = os.path.join(d, "f.txt")
        with open(base, "w") as f:
            f.write("inicial\n")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], check=True)
        # base sha
        base_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        v = cpf(12)
        with open(base, "a") as f:
            f.write(v + "\n")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-q", "-m", "add"], check=True)
        code = main(["--diff", base_sha])
        assert code == 1
        os.chdir(old)