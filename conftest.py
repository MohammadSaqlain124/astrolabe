import os
import tempfile

# point every test at a throwaway database, never the real data/astronomy.db
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "astro_test.db")

import pytest

from app.core.database import Base, engine
from app.core import models  # noqa: F401 - registers the models on Base


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
