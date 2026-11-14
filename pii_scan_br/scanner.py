"""Varredura de arquivos e diffs por CPF/CNPJ."""

import fnmatch
import os
import re
import subprocess
from dataclasses import dataclass


@dataclass
class Achado:
    arquivo: str
    linha: int
    coluna: int
    tipo: str
    mascarado: str

    def to_dict(self):
        return {
            "file": self.arquivo,
            "line": self.linha,
            "column": self.coluna,
            "type": self.tipo,
            "masked": self.mascarado,
            "masked_value": self.mascarado,
        }


# padrões de candidatos
CPF_FMT = re.compile(r"(?<![0-9A-Za-z])\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}(?![0-9A-Za-z])")
CNPJ_NUM_FMT = re.compile(r"(?<![0-9A-Za-z])\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-.\s]?\d{2}(?![0-9A-Za-z])")
DIGITS_11 = re.compile(r"(?<![0-9A-Za-z])\d{11}(?![0-9A-Za-z])")
DIGITS_14 = re.compile(r"(?<![0-9A-Za-z])\d{14}(?![0-9A-Za-z])")
ALNUM_FMT = re.compile(r"(?<![0-9A-Za-z])[0-9A-Z]{2}[.\s]?[0-9A-Z]{3}[.\s]?[0-9A-Z]{3}[/\s]?[0-9A-Z]{4}[-.\s]?\d{2}(?![0-9A-Za-z])")
ALNUM_PLAIN = re.compile(r"(?<![0-9A-Za-z])[0-9A-Z]{12}\d{2}(?![0-9A-Za-z])")

from . import validators as V


def _candidates(line: str):
    """Lista de (start, end, texto, tipo_hint) sem sobreposição."""
    raw = []
    for pat, hint in (
        (CPF_FMT, "CPF"),
        (CNPJ_NUM_FMT, "CNPJ"),
        (DIGITS_11, "CPF"),
        (DIGITS_14, "CNPJ"),
        (ALNUM_FMT, "ALNUM"),
        (ALNUM_PLAIN, "ALNUM"),
    ):
        for m in pat.finditer(line):
            raw.append((m.start(), m.end(), m.group(0), hint))
    # ordenar por start asc, len desc
    raw.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    chosen = []
    for cand in raw:
        if any(c[0] < cand[1] and cand[0] < c[1] for c in chosen):
            continue
        chosen.append(cand)
    return chosen


def _classify(text: str, hint: str):
    if hint == "CPF":
        return "CPF" if V.cpf_valido(text) else None
    if hint == "CNPJ":
        return "CNPJ" if V.cnpj_numerico_valido(text) else None
    # ALNUM
    if V.cnpj_alfanumerico_valido(text):
        return "CNPJ"
    # pode ser numérico disfarçado: deixa o candidato numérico cuidar; aqui ignora
    return None


def scan_line(line: str, arquivo: str, lineno: int):
    results = []
    if "pii-scan-br: ignore" in line:
        return results
    for start, end, text, hint in _candidates(line):
        tipo = _classify(text, hint)
        if tipo is None:
            continue
        col = start + 1
        results.append(Achado(arquivo=arquivo, linha=lineno, coluna=col, tipo=tipo, mascarado=V.mascarar(tipo, text)))
    return results


def _load_ignore(path):
    patterns = []
    if path and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                for raw in f:
                    s = raw.strip()
                    if not s or s.startswith("#"):
                        continue
                    patterns.append(s)
        except OSError:
            pass
    return patterns


def _match_ignore(relpath: str, patterns):
    rel = relpath.replace(os.sep, "/")
    for pat in patterns:
        if "**" in pat:
            rx = re.escape(pat).replace(r"\*\*", ".*").replace(r"\*", r"[^/]*")
            if re.fullmatch(rx, rel):
                return True
        else:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(os.path.basename(rel), pat):
                return True
    return False


def _is_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]


def scan_file(path: str, ignore_patterns=None, max_bytes=1048576, root=None):
    results = []
    if not os.path.isfile(path):
        return results
    try:
        size = os.path.getsize(path)
    except OSError:
        return results
    if size > max_bytes:
        return results
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return results
    if _is_binary(data):
        return results
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
    rel = os.path.relpath(path, root) if root else os.path.relpath(path)
    if ignore_patterns and _match_ignore(rel, ignore_patterns):
        return results
    for i, line in enumerate(text.splitlines(), start=1):
        results.extend(scan_line(line, rel, i))
    return results


def scan_paths(paths, ignore_file=".pii-scan-br-ignore", max_bytes=1048576):
    ignore_patterns = _load_ignore(ignore_file)
    root = os.getcwd()
    results = []
    for p in paths:
        if os.path.isdir(p):
            for dirpath, dirnames, filenames in os.walk(p):
                # prune ignored dirs? keep simple
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    results.extend(scan_file(full, ignore_patterns, max_bytes, root))
        else:
            results.extend(scan_file(p, ignore_patterns, max_bytes, root))
    results.sort(key=lambda a: (a.arquivo, a.linha, a.coluna))
    return results


def scan_diff(ref, ignore_file=".pii-scan-br-ignore", max_bytes=1048576):
    ignore_patterns = _load_ignore(ignore_file)
    try:
        proc = subprocess.run(
            ["git", "diff", f"{ref}...HEAD", "--unified=0"],
            capture_output=True, text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git nao encontrado no PATH") from exc
    if proc.returncode != 0:
        # fallback para sintaxe de dois pontos
        proc = subprocess.run(
            ["git", "diff", f"{ref}..HEAD", "--unified=0"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or "").strip() or "ref invalida ou repositorio git invalido"
            raise ValueError(msg)
    results = []
    current_file = None
    new_lineno = None
    for line in proc.stdout.splitlines():
        if line.startswith("+++ "):
            path = line[4:]
            if path.startswith("b/"):
                path = path[2:]
            if path == "/dev/null":
                current_file = None
            else:
                current_file = path
            continue
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                new_lineno = int(m.group(1))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            if current_file is not None and not _match_ignore(current_file, ignore_patterns):
                results.extend(scan_line(line[1:], current_file, new_lineno if new_lineno else 1))
            if new_lineno is not None:
                new_lineno += 1
            continue
        if line.startswith("-") and not line.startswith("---"):
            continue
        # context or empty
        if new_lineno is not None and (line.startswith(" ") or line == ""):
            new_lineno += 1
    results.sort(key=lambda a: (a.arquivo, a.linha, a.coluna))
    return results