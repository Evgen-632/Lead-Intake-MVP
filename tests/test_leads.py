import sqlite3
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import database
import logging_config
from main import app


@pytest.fixture
def environment(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    log = tmp_path / "events.log"
    monkeypatch.setattr(database, "DB_PATH", db)
    monkeypatch.setattr(logging_config, "LOG_PATH", log)
    with TestClient(app) as client:
        yield client, db, log


def test_full_lead_saved_and_logged(environment):
    client, db, log = environment
    response = client.post("/lead", json={"name": " Ирина ", "contact": " +79990000000 ", "source": " landing ", "comment": " консультация "})
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "lead_id": 1, "message": "Заявка успешно сохранена"}
    with sqlite3.connect(db) as connection:
        row = connection.execute("SELECT id, created_at, name, contact, source, comment FROM leads").fetchone()
    assert row[0] == data["lead_id"]
    assert datetime.fromisoformat(row[1]).utcoffset().total_seconds() == 0
    assert row[2:] == ("Ирина", "+79990000000", "landing", "консультация")
    content = log.read_text(encoding="utf-8")
    assert "New lead saved: 1" in content
    assert "+79990000000" not in content


def test_optional_fields_and_multiple_requests(environment):
    client, db, log = environment
    first = client.post("/lead", json={"contact": "mail@example.com"})
    second = client.post("/lead", json={"contact": "another"})
    assert first.status_code == second.status_code == 200
    assert first.json()["lead_id"] != second.json()["lead_id"]
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT name, source, comment FROM leads ORDER BY id").fetchall() == [("", "", ""), ("", "", "")]
    assert log.read_text(encoding="utf-8").count("New lead saved:") == 2


@pytest.mark.parametrize("payload", [
    {}, {"contact": ""}, {"contact": "   "}, {"contact": 123},
    {"contact": None}, {"contact": {"value": "x"}},
    {"contact": "x", "name": 1}, {"contact": "x", "source": []},
    {"contact": "x", "comment": None},
])
def test_invalid_fields(environment, payload):
    client, db, log = environment
    response = client.post("/lead", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT count(*) FROM leads").fetchone()[0] == 0
    assert not log.exists()


def test_invalid_json(environment):
    client, db, log = environment
    response = client.post("/lead", content='{broken', headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT count(*) FROM leads").fetchone()[0] == 0
    assert not log.exists()


def test_database_error(environment, tmp_path, monkeypatch):
    client, _, log = environment
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "missing" / "test.db")
    response = client.post("/lead", json={"contact": "x"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Не удалось сохранить заявку. Попробуйте позже."}
    content = log.read_text(encoding="utf-8")
    assert "ERROR" in content and "sqlite3.OperationalError" in content
    assert "New lead saved" not in content


def test_sql_input_is_data(environment):
    client, db, _ = environment
    value = "x'); DROP TABLE leads; --"
    assert client.post("/lead", json={"contact": value}).status_code == 200
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT contact FROM leads").fetchone()[0] == value
