# pii-scan-br

Encontre CPF e CNPJ (inclusive o CNPJ alfanumérico) antes que entrem no seu repositório: CLI, hook pre-commit e GitHub Action.

## Instalação

```bash
pip install git+https://github.com/YVTOMAZ/pii-scan-br@v0.1.0
```

## Uso

CLI:
```bash
pii-scan-br [ARQUIVOS...]
pii-scan-br --diff <ref>
pii-scan-br --format json
```

Pre-commit:
```yaml
- repo: https://github.com/YVTOMAZ/pii-scan-br
  rev: v0.1.0
  hooks:
    - id: pii-scan-br
```

GitHub Action:
```yaml
- uses: YVTOMAZ/pii-scan-br@v0.1.0
  with:
    base-sha: ${{ github.event.pull_request.base.sha }}
permissions:
  contents: read
```

## Supressões

- Comentário na linha: `pii-scan-br: ignore`
- Arquivo `.pii-scan-br-ignore` na raiz com padrões glob (um por linha, `#` comenta), ex.: `tests/**`
- Binários e arquivos > 1 MiB ignorados por padrão (`--max-bytes`).

## Saída

`arquivo:linha:coluna tipo valor_mascarado` (ex.: `src/x.py:12:8 CPF ***.***.**9-09`). O valor completo nunca é impresso.

## Limites

Falsos positivos/negativos possíveis. Apenas CPF e CNPJ numérico/alfanumérico são detectados; CNS, PIS/NIS, telefone, e-mail etc. fora do escopo (roadmap).

## Fonte oficial do CNPJ alfanumérico

Regra do dígito verificador conforme documentação da Receita Federal: https://www.gov.br/receitafederal/pt-br/assuntos/cadastros-e-registros-especiais/cnpj

## Projeto irmão

Complementar ao [Contextuva](https://github.com/YVTOMAZ/pii-guard-br).

## Roadmap

CNS, PIS/NIS, título de eleitor, telefone, chave PIX, e-mail; varredura de histórico Git; publicação no PyPI; GitHub Marketplace.

---

## English (short)

CLI + pre-commit hook + GitHub Action that finds CPF and CNPJ (including alphanumeric CNPJ) before they reach your repository. Python ≥3.10, no runtime dependencies. MIT.