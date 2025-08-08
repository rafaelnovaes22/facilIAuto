# Contribuindo

- Branches: feature/<escopo>, fix/<escopo>, chore/<escopo>
- Commits: Conventional Commits (feat, fix, chore, docs, refactor)
- PRs: sempre para `main`, com descrição clara
- Qualidade: `pre-commit install && pre-commit run -a`
  - Black + isort
  - Flake8 (erros críticos) e MyPy
  - Testes: `pytest -q`
- Padrões: EOL LF; config no `pyproject.toml`; evitar HTML/JS inline
- Segurança: sem segredos em commits; use `.env`/`env.example`
