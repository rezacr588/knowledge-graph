# Repository Guidelines

## Project Structure & Module Organization
- `backend/` houses the FastAPI service, retrieval modules, and utilities (e.g., `backend/main.py`, `backend/utils/document_parser.py`).
- `frontend/` contains the React client (`src/App.jsx`, component library, styles).
- `tests/` groups backend integration/unit tests; shell helpers live beside it (`test_endpoints.sh`).
- `docs/` and root markdown files capture deployment playbooks, design notes, and evaluation summaries.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` / `pip install -r requirements-dev.txt`: install runtime or dev toolchain.
- `uvicorn backend.main:app --reload`: start the API locally on port 8000.
- `npm install && npm run dev -- --host`: bootstrap and run the Vite-powered frontend at 5173.
- `pytest`: execute Python test suites with asyncio support and coverage hooks.
- `./test_endpoints.sh`: smoke-test public API routes via curl.

## Coding Style & Naming Conventions
- Python: 4-space indents, type hints, and Pydantic schemas following `CamelCase` class / `snake_case` function names.
- React: functional components with PascalCase filenames, hooks favored over class components.
- Run `black`, `flake8`, and `pylint` (see `requirements-dev.txt`) before submitting; frontend code should satisfy ESLint defaults (configure via `package.json`).

## Testing Guidelines
- Prefer `pytest` with descriptive test names like `test_ingest_pdf_extracts_text`. Place backend tests under `tests/backend/` mirroring module paths.
- API regression checks belong in `tests/integration/` or shell scripts if HTTP heavy.
- Target coverage reports when touching critical ingestion or retrieval paths; add fixtures for Neo4j/Qdrant stubs where possible.

## Commit & Pull Request Guidelines
- Commit subjects follow imperative voice (`Add document parser`, `Fix health check`). Group related backend/frontend edits in logical units.
- PRs should describe scope, testing performed (`pytest`, `npm test`, manual curl), and link to issue IDs or TODO references.
- Include screenshots or curl output when UI/API behavior changes; note configuration impacts (e.g., env var additions) explicitly.
