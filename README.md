# FastAPI Starter

A small and beginner-friendly FastAPI project focused on a simple user model and basic CRUD operations.

## What this project includes

- FastAPI app with a minimal structure
- Async SQLAlchemy setup
- SQLite for local development
- User create/list/get/update/delete endpoints
- Simple password hashing and basic dependency-based user access

## Quick start

```bash
uv sync
uv run uvicorn src.app.main:app --reload
```

Then open:

- http://127.0.0.1:8000/docs

## Environment

Create a file named `src/.env` and set the basic values you need. The project uses environment-based settings for app metadata, database connection, and security values.

## Project structure

```text
src/app/
  main.py
  api/v1/users.py
  core/
  models/
  schemas/
```

## Notes

This repository was simplified for learning purposes, so it keeps only the most essential parts of a FastAPI starter.

## License

MIT
