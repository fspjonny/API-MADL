from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madl.database import get_session
from madl.models import Account, Book, Novelist
from madl.schemas.book_schema import (
    BookPublicSchema,
    BookSchema,
    BookUpdateSchema,
    PaginatedBooksResponse,
)
from madl.schemas.message_schema import MessageSchema
from madl.security import get_current_user

router = APIRouter(prefix='/books', tags=['Books'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[Account, Depends(get_current_user)]


@router.post(
    '/new',
    status_code=HTTPStatus.CREATED,
    response_model=BookSchema,
    name='Create a new Book',
)
def create_book(
    book: BookSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_book = session.scalar(
        select(Book).where(Book.title == book.title.lower())
    )

    if db_book:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Livro já consta no MADR',
        )

    db_novelist = session.scalar(
        select(Novelist).where(Novelist.id == book.novelist_id)
    )

    if not db_novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrado',
        )

    db_book = Book(
        year=book.year, title=book.title.lower(), novelist_id=book.novelist_id
    )

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    response_model=PaginatedBooksResponse,
    name='Read and list all Books',
)
def read_books(
    session: T_Session,
    title: Optional[str] = None,
    year: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
):
    query = session.query(Book)

    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))
    if year:
        query = query.filter(Book.year == year)

    total_books = query.count()

    query = query.offset((page - 1) * per_page).limit(per_page)

    books = query.all()

    return {
        'books': books,
        'total': total_books,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_books + per_page - 1) // per_page,
    }


@router.get(
    '/{book_id}',
    status_code=HTTPStatus.OK,
    response_model=BookPublicSchema,
    name='Find one Book by id',
)
def read_one_book(book_id: int, session: T_Session):
    book = session.scalar(select(Book).where((Book.id == book_id)))

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro não consta no MADR'
        )

    return book


@router.patch(
    '/{book_id}',
    response_model=BookPublicSchema,
    name='Update a Book Data',
)
def patch_book(
    book_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
    book: BookUpdateSchema,
):
    db_book = session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro não consta no MADR'
        )

    schema_values = {'year': 'string', 'title': 'string', 'novelist_id': 0}

    book.title = book.title.lower()

    if book.novelist_id:
        db_novelist = session.scalar(
            select(Novelist).where(Novelist.id == book.novelist_id)
        )

        if not db_novelist:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Romancista não encontrado',
            )

    for key, value in book.model_dump(exclude_unset=True).items():
        if value != schema_values.get(key, None):
            setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.delete(
    '/{book_id}',
    response_model=MessageSchema,
    name='Delete one Book',
)
def delete_book(
    book_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    book = session.scalar(select(Book).where(Book.id == book_id))

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro não consta no MADR'
        )

    session.delete(book)
    session.commit()

    return {'message': 'Livro deletado no MADR'}
