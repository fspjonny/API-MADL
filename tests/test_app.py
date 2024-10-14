from http import HTTPStatus

from fastapi.testclient import TestClient

from madl.app import app


def test_root_must_returns_message():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'MADR Online!'}
