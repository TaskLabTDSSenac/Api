from datetime import datetime, timedelta, timezone

import pytest


URL = '/users/me/password'
OLD_PASSWORD = 'SenhaSegura123'


def user_snapshot(email='ana@example.com'):
    from app.database import SessionLocal
    from app.repositories.user_repository import UserRepository

    with SessionLocal() as session:
        user = UserRepository(session).get_by_email(email)
        return {key: getattr(user, key) for key in
                ('id', 'name', 'email', 'password_hash', 'created_at', 'updated_at')}


@pytest.mark.parametrize('current,new,message', [
    ('errada', 'NovaSenha456', 'Senha atual incorreta.'),
    (OLD_PASSWORD, OLD_PASSWORD, 'A nova senha deve ser diferente da senha atual.'),
])
def test_business_errors_preserve_database(client, users, current, new, message):
    before = user_snapshot()
    result = client.patch(URL, headers=users[0], json={
        'current_password': current, 'new_password': new,
    })
    assert result.status_code == 400
    assert result.json() == {'detail': message}
    assert user_snapshot() == before


@pytest.mark.parametrize('payload', [
    {'current_password': OLD_PASSWORD, 'new_password': '1234567'},
    {'current_password': OLD_PASSWORD},
    {'new_password': 'NovaSenha456'},
    {'current_password': '', 'new_password': 'NovaSenha456'},
    {'current_password': 'x' * 129, 'new_password': 'NovaSenha456'},
    {'current_password': OLD_PASSWORD, 'new_password': 'x' * 129},
    {'current_password': OLD_PASSWORD, 'new_password': 'NovaSenha456', 'user_id': 2},
    {'current_password': OLD_PASSWORD, 'new_password': 'NovaSenha456', 'email': 'bia@example.com'},
    {'current_password': OLD_PASSWORD, 'new_password': 'NovaSenha456', 'confirm_password': 'NovaSenha456'},
    {'current_password': {'current_password': 'SecretCurrent'}, 'new_password': ['SecretNew']},
    [{'current_password': 'SecretCurrent', 'new_password': 'SecretNew'}],
])
def test_validation_redacts_secrets_and_preserves_database(client, users, payload, caplog):
    before = user_snapshot()
    result = client.patch(URL, headers=users[0], json=payload)
    assert result.status_code == 422
    assert all('input' not in error for error in result.json()['detail'])
    for secret in [OLD_PASSWORD, '1234567', 'NovaSenha456', 'SecretCurrent', 'SecretNew', 'x' * 129]:
        assert secret not in result.text
        assert secret not in caplog.text
    assert user_snapshot() == before


@pytest.mark.parametrize('new_password', ['12345678', '  NovaSenha456  '])
def test_change_password_preserves_accounts_tasks_and_existing_token(client, users, task, new_password, caplog):
    from app.security.password import verify_password

    before = user_snapshot()
    other_before = user_snapshot('bia@example.com')
    result = client.patch(URL, headers=users[0], json={
        'current_password': OLD_PASSWORD, 'new_password': new_password,
    })
    assert result.status_code == 200
    assert result.json() == {'detail': 'Senha alterada com sucesso.'}
    after = user_snapshot()
    assert after['password_hash'] != before['password_hash']
    assert after['password_hash'] != new_password
    assert after['password_hash'].startswith('$argon2id$')
    assert verify_password(new_password, after['password_hash'])
    assert after['updated_at'] > before['updated_at']
    for key in ('id', 'name', 'email', 'created_at'):
        assert after[key] == before[key]
    assert user_snapshot('bia@example.com') == other_before
    for password, expected in [(OLD_PASSWORD, 401), (new_password, 200)]:
        login = client.post('/auth/login', json={'email': before['email'], 'password': password})
        assert login.status_code == expected
    assert client.post('/auth/login', json={'email': 'bia@example.com', 'password': OLD_PASSWORD}).status_code == 200
    assert client.get('/users/me', headers=users[0]).json()['id'] == before['id']
    assert client.get('/tasks', headers=users[0]).json() == [task]
    if new_password != new_password.strip():
        assert client.post('/auth/login', json={'email': before['email'], 'password': new_password.strip()}).status_code == 401
        # A senha atual também precisa preservar os espaços na troca seguinte.
        assert client.patch(URL, headers=users[0], json={
            'current_password': new_password, 'new_password': 'OutraSenha789',
        }).status_code == 200
    assert OLD_PASSWORD not in caplog.text
    assert new_password not in caplog.text


@pytest.mark.parametrize('token_kind', ['missing', 'invalid', 'expired'])
def test_authentication_required(client, users, token_kind):
    import jwt
    from app.config import settings

    before = user_snapshot()
    headers = {}
    if token_kind == 'invalid':
        headers = {'Authorization': 'Bearer invalid'}
    elif token_kind == 'expired':
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {'sub': str(before['id']), 'iat': now - timedelta(minutes=2), 'exp': now - timedelta(minutes=1)},
            settings.jwt_secret_key.get_secret_value(), algorithm='HS256',
        )
        headers = {'Authorization': f'Bearer {token}'}
    result = client.patch(URL, headers=headers, json={
        'current_password': OLD_PASSWORD, 'new_password': 'NovaSenha456',
    })
    assert result.status_code == 401
    assert result.headers['www-authenticate'] == 'Bearer'
    assert user_snapshot() == before


def test_repository_rolls_back_on_failure(client, users, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError
    from app.database import SessionLocal
    from app.repositories.user_repository import UserRepository

    before = user_snapshot()
    with SessionLocal() as session:
        repository = UserRepository(session)
        user = repository.get_by_id(before['id'])

        def fail_commit():
            raise SQLAlchemyError('Simulated persistence failure')

        monkeypatch.setattr(session, 'commit', fail_commit)
        with pytest.raises(SQLAlchemyError):
            repository.update_password(user, 'unused-test-hash')
        assert user.password_hash == before['password_hash']
        assert user.updated_at == before['updated_at']
    assert user_snapshot() == before


def test_password_schema_and_swagger(client):
    from app.schemas.user_schema import PasswordChangeRequest

    data = PasswordChangeRequest(current_password='SecretCurrent', new_password='SecretNew')
    assert 'SecretCurrent' not in repr(data)
    assert 'SecretNew' not in repr(data)
    operation = client.get('/openapi.json').json()['paths'][URL]['patch']
    assert operation['security'] == [{'HTTPBearer': []}]
    assert all(str(code) in operation['responses'] for code in [200, 400, 401, 422])
