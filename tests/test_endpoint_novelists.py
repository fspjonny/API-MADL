from http import HTTPStatus


def test_deny_create_novelist_without_permissions(client):
    response = client.post(
        '/novelists/new',
        json={
            'name': 'Jorge Amado',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_allow_create_novelist_with_permissions(client, token):
    response = client.post(
        '/novelists/new',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Jorge Amado',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'jorge amado',
    }


def test_get_one_novelist(client, novelist):
    response = client.get(f'novelists/{novelist.id}')
    assert response.status_code == HTTPStatus.OK


def test_get_one_inexistent_novelist(client):
    response = client.get('novelists/1')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}


def test_list_all_novelists_but_list_empty(client):
    response = client.get('novelists/list')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'novelists': [],
        'total': 0,
        'page': 1,
        'per_page': 20,
        'total_pages': 0,
    }


def test_list_all_novelists_list_with_novelist(client, novelist):
    response = client.get('novelists/list')
    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert 'novelists' in response_data
    assert len(response_data['novelists']) > 0
    assert response_data['novelists'][0]['id'] == novelist.id


def test_if_novelist_exists(client, novelist, token):
    response = client.post(
        '/novelists/new',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': novelist.name,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista já consta no MADR'}


def test_read_novelist_filter_by_name(client, novelist):
    response = client.get(
        '/novelists/list',
        params={'name': novelist.name},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['novelists']) == 1
    assert data['novelists'][0]['name'] == novelist.name


def test_patch_novelist_error(client, token):
    response = client.patch(
        '/novelists/1',
        json={
            'name': 'string',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}


def test_patch_novelist(client, novelist, token):
    response = client.patch(
        f'/novelists/{novelist.id}',
        json={
            'name': 'casemiro de abreu',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'casemiro de abreu'


def test_delete_novelist(client, novelist, token):
    response = client.delete(
        f'/novelists/{novelist.id}',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancista deletado no MADR'}


def test_delete_novelist_error(client, token):
    response = client.delete(
        '/novelists/2', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}
