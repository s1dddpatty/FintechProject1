import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.dependencies import get_db, get_model_registry
from src.api.main import app
from src.db.base import Base
from src.ml.registry import ModelRegistry


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def temp_registry():
    d = tempfile.mkdtemp()
    registry = ModelRegistry(registry_dir=d)
    yield registry
    shutil.rmtree(d)


@pytest.fixture
def client(db_session, temp_registry):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_registry():
        return temp_registry

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_model_registry] = override_get_registry

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
