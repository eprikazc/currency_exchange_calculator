from src.crud_utils import create_currency
from src.models_sqla import Currency


def test_list_currencies(client, db):
    usd = create_currency(db, code="USD")
    resp = client.get("/currencies/")
    assert resp.status_code == 200
    assert resp.json() == [{"code": "USD", "id": usd.id}]


def test_create_currency(client, db):
    resp = client.post("/currencies/", json={"code": "USD"})
    assert resp.status_code == 201
    currency = db.query(Currency).filter_by(code="USD").first()
    assert resp.json() == {"code": "USD", "id": currency.id}


def test_update_currency(client, db):
    usd = create_currency(db, code="USD")
    resp = client.put(f"/currencies/{usd.id}", json={"code": "CAD"})
    assert resp.status_code == 200
    assert resp.json() == {"code": "CAD", "id": usd.id}
    usd = db.query(Currency).filter_by(id=usd.id).first()
    assert usd.code == "CAD"


def test_get_currency(client, db):
    usd = create_currency(db, code="USD")
    resp = client.get(f"/currencies/{usd.id}")
    assert resp.status_code == 200
    assert resp.json() == {"code": "USD", "id": usd.id}


def test_delete_currency(client, db):
    usd = create_currency(db, code="USD")
    resp = client.delete(f"/currencies/{usd.id}")
    assert resp.status_code == 204
    usd = db.query(Currency).filter_by(id=usd.id).first()
    assert usd is None
