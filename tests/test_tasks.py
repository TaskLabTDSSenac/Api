from datetime import datetime

import pytest


OPERATIONS = [("put", ""), ("patch", "/complete"), ("delete", "")]


def operate(client, method, suffix, task_id, headers):
    options = {"json": {"title": "Título atualizado"}} if method == "put" else {}
    return client.request(method, f"/tasks/{task_id}{suffix}", headers=headers, **options)


def test_edit_task(client, users, task):
    response = client.put(
        f"/tasks/{task['id']}", headers=users[0],
        json={"title": "  Título atualizado  ", "description": "Nova descrição"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated['title'] == "Título atualizado"
    assert updated['description'] == "Nova descrição"
    assert updated['id'] == task['id']
    assert updated['completed'] is False
    assert updated['created_at'] == task['created_at']
    assert datetime.fromisoformat(updated['updated_at']) > datetime.fromisoformat(task['updated_at'])
    assert updated['updated_at'].endswith('Z')
    assert 'user_id' not in updated
    assert client.get(f"/tasks/{task['id']}", headers=users[0]).json() == updated


@pytest.mark.parametrize('payload', [
    {}, {'title': ''}, {'title': '  '}, {'title': 'ab'}, {'title': 'x' * 151},
    {'title': 'Valid', 'description': 'x' * 501},
    {'title': 'Valid', 'completed': True}, {'title': 'Valid', 'user_id': 2},
    {'title': 'Valid', 'id': 2}, {'title': 'Valid', 'updated_at': '2026-01-01'},
])
def test_invalid_edit_does_not_change_task(client, users, task, payload):
    url = f"/tasks/{task['id']}"
    assert client.put(url, headers=users[0], json=payload).status_code == 422
    assert client.get(url, headers=users[0]).json() == task


def test_edit_three_characters_clears_omitted_description(client, users, task):
    response = client.put(f"/tasks/{task['id']}", headers=users[0], json={'title': '  abc  '})
    assert response.status_code == 200
    assert response.json()['title'] == 'abc'
    assert response.json()['description'] is None


def test_complete_and_reject_repetition(client, users, task):
    url = f"/tasks/{task['id']}/complete"
    response = client.patch(url, headers=users[0])
    assert response.status_code == 200
    completed = response.json()
    assert completed['completed'] is True
    assert completed['title'] == task['title']
    assert completed['description'] == task['description']
    assert datetime.fromisoformat(completed['updated_at']) > datetime.fromisoformat(task['updated_at'])
    repeated = client.patch(url, headers=users[0])
    assert repeated.status_code == 400
    assert repeated.json() == {'detail': 'A tarefa já está concluída.'}
    assert client.get(f"/tasks/{task['id']}", headers=users[0]).json() == completed
    edited = client.put(f"/tasks/{task['id']}", headers=users[0], json={'title': 'Still completed'})
    assert edited.status_code == 200
    assert edited.json()['completed'] is True


def test_delete_is_physical_and_returns_empty_response(client, users, task):
    from app.database import SessionLocal
    from app.models.task import Task

    response = client.delete(f"/tasks/{task['id']}", headers=users[0])
    assert response.status_code == 204
    assert response.content == b''
    assert client.get(f"/tasks/{task['id']}", headers=users[0]).status_code == 404
    assert client.get('/tasks', headers=users[0]).json() == []
    with SessionLocal() as session:
        assert session.get(Task, task['id']) is None


@pytest.mark.parametrize('method,suffix', OPERATIONS)
def test_missing_and_other_users_task_are_not_found(client, users, task, method, suffix):
    missing = operate(client, method, suffix, 999999, users[0])
    other = operate(client, method, suffix, task['id'], users[1])
    assert missing.status_code == other.status_code == 404
    assert missing.json() == other.json() == {'detail': 'Tarefa não encontrada.'}
    assert client.get(f"/tasks/{task['id']}", headers=users[0]).json() == task


@pytest.mark.parametrize('method,suffix', OPERATIONS)
@pytest.mark.parametrize('headers', [{}, {'Authorization': 'Bearer invalid'}])
def test_authentication_required(client, users, task, method, suffix, headers):
    response = operate(client, method, suffix, task['id'], headers)
    assert response.status_code == 401
    assert response.headers['www-authenticate'] == 'Bearer'
    assert client.get(f"/tasks/{task['id']}", headers=users[0]).json() == task


def test_existing_routes_and_swagger(client, users, task):
    assert client.get('/health').json() == {'status': 'ok'}
    assert client.get('/users/me', headers=users[0]).json()['email'] == 'ana@example.com'
    assert client.get('/tasks', headers=users[0]).json() == [task]
    assert client.get('/tasks', headers=users[1]).json() == []
    assert client.get('/docs').status_code == 200
    paths = client.get('/openapi.json').json()['paths']
    for method, suffix in OPERATIONS:
        operation = paths['/tasks/{id}' + suffix][method]
        assert operation['security'] == [{'HTTPBearer': []}]
    assert 'content' not in paths['/tasks/{id}']['delete']['responses']['204']
    assert 'requestBody' not in paths['/tasks/{id}/complete']['patch']
