from pathlib import Path

from app.core.database import Base, engine
from app.core import models  # noqa: F401 - imported so the model registers on Base


def main():
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
    print("Database ready. Tables:", list(Base.metadata.tables))


if __name__ == "__main__":
    main()