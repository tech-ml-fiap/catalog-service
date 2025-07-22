import importlib

import pytest


@pytest.mark.usefixtures("monkeypatch")
def test_get_repo_returns_same_instance(monkeypatch):
    module_path = "app.adapters.driver.dependencies.di"

    di = importlib.reload(importlib.import_module(module_path))

    created = 0

    class DummyRepo:
        pass

    def _dummy_ctor():
        nonlocal created
        created += 1
        return DummyRepo()

    monkeypatch.setattr(di, "MongoProductRepository", _dummy_ctor)

    repo1 = di.get_repo()
    repo2 = di.get_repo()

    assert repo1 is repo2
    assert created == 1
    assert isinstance(repo1, DummyRepo)
