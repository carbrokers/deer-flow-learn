# Repository Guidelines

## Project Structure & Module Organization
DeerFlow is split into a Python backend and a Next.js frontend. Use `backend/` for agent runtime, gateway APIs, sandboxing, and backend tests in `backend/tests/`. Use `frontend/` for the app shell, UI components, and web tests in `frontend/tests/e2e/`. Shared repo-level tooling lives in `scripts/`, Docker and nginx assets live in `docker/`, and reusable skills live in `skills/public/`. Configuration starts from `config.example.yaml` and `extensions_config.example.json`.

## Build, Test, and Development Commands
Run `make install` once from the repo root to install backend/frontend dependencies and pre-commit hooks. Use `make dev` to start the full local stack behind nginx at `http://localhost:2026`. For Docker-based development, use `make docker-init` then `make docker-start`.

For targeted work:
- `cd backend && make test` runs Python unit tests with `pytest`.
- `cd backend && make format` applies `ruff` fixes and formatting.
- `cd frontend && pnpm check` runs ESLint plus TypeScript checks.
- `cd frontend && pnpm test` runs Vitest.
- `cd frontend && pnpm test:e2e` runs Playwright end-to-end tests.

## Coding Style & Naming Conventions
Backend code targets Python 3.12+, uses `ruff`, and follows existing module patterns in `backend/app/` and `backend/packages/`. Frontend code uses TypeScript, React 19, Next.js, ESLint, and Prettier with the Tailwind plugin. Match the surrounding style: `snake_case` for Python files and functions, `PascalCase` for React components, and `kebab-case` for route folders where Next.js expects it. Keep changes local to the subsystem you are touching.

## Testing Guidelines
Add or update tests with every behavior change. Backend tests belong in `backend/tests/test_<feature>.py`. Frontend unit tests should live near the relevant feature or in the existing frontend test layout; E2E specs belong in `frontend/tests/e2e/*.spec.ts`. Run the smallest relevant test set first, then broader checks before opening a PR.

## Commit & Pull Request Guidelines
Recent history follows Conventional Commit-style prefixes such as `feat(...)`, `fix(...)`, and `chore(...)`. Keep commit subjects imperative and scoped when useful, for example `fix(sandbox): prevent symlink escapes`. PRs should describe the user-visible change, list validation performed, link related issues, and include screenshots or recordings for frontend changes.

## Configuration & Contributor Notes
Do not commit real secrets; start from `.env.example` and `config.example.yaml`. Run `make doctor` if local setup looks inconsistent. For backend architecture and deeper agent-specific implementation rules, read `backend/AGENTS.md` before making nontrivial backend changes.
