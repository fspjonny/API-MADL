import factory
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from madl.app import app
from madl.database import get_session
from madl.models import Account, Book, Novelist, table_registry
from madl.security import get_password_hash

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = Account

    username = factory.Sequence(lambda n: f'Tester{n}')
    email = factory.LazyAttribute(
        lambda obj: f'{obj.username}@email.com'.lower()
    )
    password = factory.LazyAttribute(lambda obj: f'{obj.username}'.lower())


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    year = factory.Faker('year')
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4).lower())
    novelist_id = 1
    # novelist_id = factory.Sequence(lambda n: n + 1)


class NovelistFactory(factory.Factory):
    class Meta:
        model = Novelist

    name = factory.LazyAttribute(
        lambda _: f'{fake.first_name().lower()} {fake.last_name().lower()}'
    )


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())
        with _engine.begin():
            yield _engine


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    password = 'tester'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    # Um 'monkey patch' para os testes
    # não testarem em um hash, mas sim uma senha em texto
    user.clean_password = 'tester'

    return user


@pytest.fixture
def other_user(session):
    password = 'tester'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'tester'

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def book(session):
    book = BookFactory()
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@pytest.fixture
def novelist(session):
    writter = NovelistFactory()
    session.add(writter)
    session.commit()
    session.refresh(writter)
    return writter
