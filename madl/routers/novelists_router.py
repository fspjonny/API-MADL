from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madl.database import get_session
from madl.models import Account, Novelist
from madl.schemas.message_schema import MessageSchema
from madl.schemas.novelist_schema import (
    NovelistPublicSchema,
    NovelistSchema,
    NovelistUpdateSchema,
    PaginatedNovelistsResponse,
)
from madl.security import get_current_user
from madl.utils import sanitize_name

router = APIRouter(prefix='/novelists', tags=['Novelists'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[Account, Depends(get_current_user)]


@router.post(
    '/new',
    status_code=HTTPStatus.CREATED,
    response_model=NovelistSchema,
    name='Create an new Novelist',
)
def create_novelist(
    novelist: NovelistSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_novelist = session.scalar(
        select(Novelist).where(Novelist.name == sanitize_name(novelist.name))
    )

    if db_novelist:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista já consta no MADR',
        )

    db_novelist = Novelist(name=sanitize_name(novelist.name))

    session.add(db_novelist)
    session.commit()
    session.refresh(db_novelist)

    return db_novelist


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    response_model=PaginatedNovelistsResponse,
    name='Read and list all Novelists',
)
def read_novelists(
    session: T_Session,
    name: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
):
    query = session.query(Novelist)

    if name:
        query = query.filter(Novelist.name.ilike(f'%{name}%'))

    total_novelists = query.count()

    query = query.offset((page - 1) * per_page).limit(per_page)

    novelists = query.all()

    return {
        'novelists': novelists,
        'total': total_novelists,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_novelists + per_page - 1) // per_page,
    }


@router.get(
    '/{novelist_id}',
    status_code=HTTPStatus.OK,
    response_model=NovelistPublicSchema,
    name='Find one Novelist by id',
)
def read_one_novelist(novelist_id: int, session: T_Session):
    novelist = session.scalar(
        select(Novelist).where((Novelist.id == novelist_id))
    )

    if not novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR',
        )

    return novelist


@router.patch(
    '/{novelist_id}',
    response_model=NovelistPublicSchema,
    name='Update an Novelist',
)
def patch_novelist(
    novelist_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
    novelist: NovelistUpdateSchema,
):
    db_novelist = session.scalar(
        select(Novelist).where(Novelist.id == novelist_id)
    )

    if not db_novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR',
        )

    schema_values = {'name': 'string'}

    novelist.name = sanitize_name(novelist.name)

    for key, value in novelist.model_dump(exclude_unset=True).items():
        # Verifica se o valor não é igual ao valor padrão do schema
        if value != schema_values.get(key, None):
            setattr(db_novelist, key, value)

    session.add(db_novelist)
    session.commit()
    session.refresh(db_novelist)

    return db_novelist


@router.delete(
    '/{novelist_id}',
    response_model=MessageSchema,
    name='Delete an Novelist',
)
def delete_novelist(
    novelist_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    novelist = session.scalar(
        select(Novelist).where(Novelist.id == novelist_id)
    )

    if not novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR',
        )

    session.delete(novelist)
    session.commit()

    return {'message': 'Romancista deletado no MADR'}
