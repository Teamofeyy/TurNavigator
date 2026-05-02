from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "travelcontext-test.db"
    database_url = f"sqlite:///{database_path}"
    os.environ["DATABASE_URL"] = database_url

    import app.models  # noqa: F401
    from app.db import Base, configure_database, get_engine
    from app.main import create_app

    configure_database(database_url)
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
