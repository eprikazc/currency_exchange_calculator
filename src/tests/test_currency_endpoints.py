from src.models_sqla import Currency


def test_list_currencies(client, db):
    usd = Currency(code="USD")
    db.add(usd)
    db.commit()
    resp = client.get("/currencies/")
    assert resp.status_code == 200
    assert resp.json() == [{"code": "USD", "id": usd.id}]
