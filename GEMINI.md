# Project Instructions

## Project
LangGraph refund-approval agent built with Python and LangGraph.

## Tech Stack
- Python 3.13
- LangGraph
- pytest
- .venv

## Decisions & Architecture
- The LLM only parses text and never decides; policy lives in plain functions.
- Amounts are integer rupees.
- The human answer must be exactly "approve" or "reject", and anything else rejects.

## Engineering Rules & Conventions
- **Virtual Environment (.venv):** Always use the project's `.venv` virtual environment for running python and pytest (`.venv\Scripts\python`, `.venv\Scripts\pytest`).
- **Test-Driven Development:** Always write tests before implementing features or bug fixes.
- **Modularity:** Keep functions small, focused, and single-responsibility.
- **Environment Protection:** Never edit `.env` files directly or commit secrets.
- **Dependencies:** Always ask the user before installing any new packages.
- **Targeted Edits:** Prefer small targeted edits over rewriting whole files. Do exactly the step requested, then stop and wait.
- **Git & File Safety:** Never run `git checkout`, `git restore`, `git reset`, or `git clean` without asking the user first. Never delete files without asking.
- **Testing Rule:** Do not run the full test suite until instructed.

## Commands
- **Install Dependencies:**
  - `pip install -r requirements.txt`
- **Run Tests:**
  - `.venv\Scripts\pytest`
