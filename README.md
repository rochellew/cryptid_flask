# Cryptids of the World

A Flask frontend for browsing and managing cryptid sightings, backed by a FastAPI service.

## Requirements
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A running instance of the FastAPI backend


## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create a `.env` file from the example:

```bash
cp .env.example .env
```

3. Fill in your `.env` values - generates a secret key with:

```bash
uv run flask shell
>>> import secrets
>>> secrets.token_hex(32)
```

### Running

```bash
uv run flask run
```
