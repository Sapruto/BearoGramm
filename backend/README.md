# BearoGramm Back-End

## Setup:
### Prerequisites
- **PostgreSQL**
- **Redis**

### 1. Clone the repository

```sh
git clone https://github.com/Sapruto/BearoGramm.git
cd BearoGramm
```

### 2. Set up the environment

Requires **Python 3.12**.

```sh
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate.ps1
pip install -r requirements.txt
```

### 3. Configure .env

Create your own `.env` file based on `.env.example`


### 4. Run the application

```sh
python run.py
```

## Migrations:
Schema is managed by Alembic.

To reset a dev database: delete the `*.db` file and run `alembic upgrade head` again.

## Environments:
| | Dev | Production |
|---|---|---|
| **Database** | SQLite (`data/test.db`) | PostgreSQL |
| **Switch by** | `ENV != "production"` | `ENV == "production"` |

Set `ENV` in `.env` to switch.

## Testing:
```sh
pytest
pytest --cov=src
```