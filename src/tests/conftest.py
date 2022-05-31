import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from src.app import app
from src.deps import get_db
from src.sqla_base import Base


@pytest.fixture
def engine():
    test_db_url = os.environ["SQLALCHEMY_DATABASE_URL"] + "_test"
    if not database_exists(test_db_url):
        create_database(test_db_url)
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db(engine):
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()  # noqa: F841
    # bind an individual Session to the connection
    db = Session(bind=connection)
    yield db
    db.rollback()
    connection.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
