from sqlalchemy import select
from sqlalchemy.orm import Session

from madl.database import get_session
from madl.models import Account


def test_create_user(session):
    new_user = Account(
        username='fabio', email='fabio@email.com', password='fabiopass'
    )
    session.add(new_user)
    session.commit()

    user = session.scalar(select(Account).where(Account.username == 'fabio'))

    assert user.username == 'fabio'


def test_get_session(session, engine, mocker):
    mocker.patch('madr.database.engine', engine)

    session_generator = get_session()
    generated_session = next(session_generator)

    assert isinstance(generated_session, Session)
    assert generated_session.bind.url == engine.url
    session_generator.close()
