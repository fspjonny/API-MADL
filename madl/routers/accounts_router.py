from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madl.database import get_session
from madl.models import Account
from madl.schemas.account_schema import AccountPublicSchema, AccountSchema
from madl.schemas.message_schema import MessageSchema
from madl.security import get_current_user, get_password_hash
from madl.utils import sanitize_email, sanitize_name

router = APIRouter(prefix='/accounts', tags=['Accounts'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[Account, Depends(get_current_user)]


@router.post(
    '/user',
    status_code=HTTPStatus.CREATED,
    response_model=AccountPublicSchema,
    name='Create an new Account User',
)
def create_user(user: AccountSchema, session: T_Session):
    db_user = session.scalar(
        select(Account).where(
            (Account.username == user.username) | (Account.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Conta já consta no MADR',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Conta já consta no MADR',
            )

    hashed_password = get_password_hash(user.password)

    db_user = Account(
        username=sanitize_name(user.username),
        email=sanitize_email(user.email),
        password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


# Implementado, Mas não está em uso por regra do projeto final.
# @router.get(
#     '/list',
#     status_code=HTTPStatus.OK,
#     response_model=AccountListSchema,
#     name='Read and list all Users Accounts',
# )
# def read_users(session: T_Session, skip: int = 0, limit: int = 100):
#     users = session.scalars(select(Account).offset(skip).limit(limit)).all()
#     total_users = session.query(Account).count()
#     return {'accounts': users, 'total': total_users}


# Implementado, Mas não está em uso por regra do projeto final.
# @router.get(
#     '/{user_id}',
#     status_code=HTTPStatus.OK,
#     response_model=AccountPublicSchema,
#     name='Find one User account by id',
# )
# def read_one_user(user_id: int, session: T_Session):
#     user = session.scalar(select(Account).where((Account.id == user_id)))

#     if not user:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='Conta não encontrada'
#         )

#     return user


@router.put(
    '/user/{user_id}',
    response_model=AccountPublicSchema,
    name='Update an User Data',
)
def update_user(
    user_id: int,
    user: AccountSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Não autorizado',
        )

    current_user.username = sanitize_name(user.username)
    current_user.email = sanitize_email(user.email)
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete(
    '/user/{user_id}',
    response_model=MessageSchema,
    name='Delete an User Account',
)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Não autorizado',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'Conta deletada com sucesso'}
