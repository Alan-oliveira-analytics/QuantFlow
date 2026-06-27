from pathlib import Path

def find_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Raiz do projeto não encontrada")



# config/paths.py
BASE_DIR = find_project_root()
DATA_DIR  = BASE_DIR / 'data'
DB_DIR    = BASE_DIR / 'database'
DOCS_DIR  = BASE_DIR / 'docs'
ENV_PATH = BASE_DIR / '.env'