# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.1] - 2026-11-14

### Fixed
- `--diff` no longer reports "no findings" (exit 0) when the git ref is invalid, the directory is not a git repository, or `git` is missing; it now exits with code 2 and an error message (#3).

### Changed
- Stronger tests: exact masking assertion, exit code 2, full value never printed to stdout/stderr, removed lines ignored by `--diff` (#3).
- Version consistency test between `__version__` and package metadata.

## [0.1.0] - 2026-11-14

### Added
- Initial release: CPF and CNPJ (numeric and alphanumeric) detection with DV validation.
- CLI `pii-scan-br`, pre-commit hook and composite GitHub Action.
- Suppressions, binary/size limits, JSON output.