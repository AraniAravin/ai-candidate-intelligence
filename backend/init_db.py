"""
init_db.py
Creates all tables defined in models.py inside PostgreSQL.
"""

import models  # noqa: F401 — import ensures models are registered with Base
from database import Base, engine

if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")