# AGENTS.md — Agent-Infra-V1.0.1

## Project Overview
Python library for validating architecture/infrastructure drawing metadata against international standards (ISO, EN, DIN, ANSI, BSI) and EvoTransDigi-specific requirements.

## Running the App
```bash
docker compose -f docker-compose.base44.yml up -d --build
```
The web interface (Flask) serves on port 3000 with live reload via `debug=True`.

## Architecture
- **Core library**: `agents/international_standards/` — the `InternationalStandardsAgent` class and per-standard validators.
- **Config**: `src/config/standards_config.yaml` (standard definitions) and `src/config/evotransdigi_config.yaml` (EvoTransDigi rules + compliance levels).
- **Web UI**: `web_app.py` (Flask) + `templates/index.html` — a thin wrapper around the core library for interactive validation.
- **Dependencies**: Only `flask`, `pyyaml`, `pydantic` are needed for the web app (see `requirements-base44.txt`). The full `requirements.txt` includes `ezdxf`, `pyautocad`, etc. which are not used at runtime and fail on Linux.

## Key APIs
- `agent.get_supported_standards()` → list of all standard version strings.
- `agent._validate_against_standard(metadata, standard)` → `ValidationResult` with errors/warnings/info.
- `agent.evotransdigi_validator.validate_metadata(metadata, level)` → EvoTransDigi-specific validation.

## Bugs Fixed for Runtime
- `agent.py`: `ISOStandard` and `ENStandard` constructor calls were missing required `publication_date` argument.
- `agent.py`: `EvoTransDigiValidator` was initialized with an `AgentConfig` object instead of the `evotransdigi_config` dict (3 call sites).
- `evotransdigi_config.yaml`: `allowed_characters` used invalid YAML escape `\-` in a double-quoted string; switched to single quotes.

## Verifying
- `curl localhost:3000/` returns the web UI.
- `curl localhost:3000/api/standards` returns the supported standards list.
- Load the example config via the "Load Example" button and click "Validate All Standards".
