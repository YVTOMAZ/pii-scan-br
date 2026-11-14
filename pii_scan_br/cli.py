"""CLI pii-scan-br."""

import argparse
import json
import sys

from . import scanner


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pii-scan-br", description="Detecta CPF e CNPJ em arquivos.")
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("--diff", dest="diff", default=None, help="varre linhas adicionadas em git diff <ref>...HEAD")
    parser.add_argument("--format", dest="fmt", choices=["text", "json"], default="text")
    parser.add_argument("--max-bytes", type=int, default=1048576)
    parser.add_argument("--ignore-file", default=".pii-scan-br-ignore")
    args = parser.parse_args(argv)

    try:
        if args.diff:
            achados = scanner.scan_diff(args.diff, ignore_file=args.ignore_file, max_bytes=args.max_bytes)
        else:
            paths = args.files if args.files else ["."]
            achados = scanner.scan_paths(paths, ignore_file=args.ignore_file, max_bytes=args.max_bytes)
    except Exception as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2

    if args.fmt == "json":
        print(json.dumps([a.to_dict() for a in achados], ensure_ascii=False, indent=2))
    else:
        for a in achados:
            print(f"{a.arquivo}:{a.linha}:{a.coluna} {a.tipo} {a.mascarado}")

    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())