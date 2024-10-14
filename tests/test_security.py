from http import HTTPStatus

import jwt
import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from jwt import decode
from pwdlib import PasswordHash

from madl.security import (
    Session,
    create_access_token,
    get_current_user,
    get_password_hash,
    settings,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded['test'] == data['test']
    assert decoded['exp']  # Testa se o valor de exp foi adicionado ao token


def test_make_str_password_in_str_hash():
    hashmaker = PasswordHash.recommended()
    pass_to_hash = 'mypassword'
    pass_hashed = get_password_hash(pass_to_hash)

    assert hashmaker.verify(pass_to_hash, pass_hashed) is True
    assert verify_password(pass_to_hash, pass_hashed) is True


def test_get_token(client, user):
    response = client.post(
        'auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_if_jwt_invalid_token(client):
    response = client.delete(
        'accounts/user/1', headers={'Authorization': 'Bearer token-invalido'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_token_expired_after_time(client, user):
    with freeze_time('2024-08-03 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2024-08-03 13:01:00'):
        response = client.put(
            f'/accounts/user/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'nobody',
                'email': 'nobody@email.com',
                'password': 'nobodypassword',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Não autorizado'}


def test_token_inexistent_user(client):
    response = client.post(
        '/auth/token',
        data={'username': 'no_user@email.com', 'password': 'nouserpassword'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email ou senha incorretos'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email ou senha incorretos'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2024-08-03 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2024-08-03 13:01:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Não autorizado'}


@pytest.mark.asyncio
async def test_missing_sub_in_token(session: Session):
    token = jwt.encode(
        {}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )  # Token sem sub

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(session=session, token=token)

    assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate credentials'


@pytest.mark.asyncio
async def test_user_not_found_in_db(session: Session):
    token = jwt.encode(
        {'sub': 'carmem'}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(session=session, token=token)

    assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate credentials'
