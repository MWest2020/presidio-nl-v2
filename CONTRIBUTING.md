# Contributing Guidelines

## Development & Coding Standards

### Tools & Workflow

- **Linter:**  
  - Gebruik [`ruff`](https://github.com/astral-sh/ruff) als linter en formatter (geschreven in Rust, supersnel).
  - **Formatter:** `ruff format` is de standaard formatter. Laat je editor automatisch formatteren bij opslaan.
- **Type Checking:**  
  - Gebruik [`mypy`](https://mypy-lang.org/) voor type checking.
  - **Let op:** De mypy-daemon is traag; gebruik de CLI (`mypy .`) in CI/CD of handmatig.
- **Docstrings & Documentatie:**  
  - Gebruik Sphinx-style docstrings voor alle publieke functies, klassen en modules.
  - Genereer documentatie met Sphinx indien gewenst.
- **Package Management:**  
  - Gebruik [`uv`](https://github.com/astral-sh/uv) als package manager voor dependency management en virtuele omgevingen.
  - Alle tools en dependencies worden beheerd via `pyproject.toml`.
- **Testing:**  
  - Gebruik [`pytest`](https://docs.pytest.org/) voor alle unittests en integratietests.
  - Tests staan in de `tests/`-directory en dekken zowel de engine als de API.
- **CI/CD:**  
  - Linting, type checking en tests worden automatisch uitgevoerd in de CI/CD pipeline.
  - Gebruik `mypy` via de CLI in CI, niet als daemon.

### Best Practices

- **Code moet altijd ruff-clean zijn** (geen linter errors/warnings).
- **Alle publieke functies en klassen hebben een duidelijke docstring.**
- **Type hints zijn verplicht** voor alle functie-argumenten en return types.
- **Elke nieuwe feature of bugfix krijgt een of meer pytest-tests.**
- **Voeg dependencies alleen toe via `pyproject.toml` en installeer met `uv`.**
- **Gebruik geen print-debugging in productiecode; gebruik logging indien nodig.**
- **Houd de codebase Python 3.12+ compatible.**

---

**Voorbeeld workflow voor contributors:**

1. Fork & clone de repo.
2. Installeer dependencies met `uv venv && uv pip install -r requirements.txt` of direct via `uv pip install .`
3. Codeer je feature/fix, commit met duidelijke boodschap.
4. Run lokaal:  
   - `ruff check .`  
   - `ruff format .`  
   - `mypy .`  
   - `pytest`
5. Voeg docstrings toe waar nodig.
6. Maak een pull request. 