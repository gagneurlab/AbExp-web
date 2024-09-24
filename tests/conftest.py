import pytest
from pathlib import Path
from abexp_web import create_app
from abexp_web.db import init_db


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(Path(request.fspath.dirname).parent)


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        init_db()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
