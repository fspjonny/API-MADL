from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from madl.routers import (
    accounts_router,
    auth_router,
    books_router,
    novelists_router,
)
from madl.schemas.message_schema import MessageSchema

tags_metadata = [
    {
        'name': 'Accounts',
        'description': 'Create and manage users accounts.',
    },
    {
        'name': 'Novelists',
        'description': 'Manage and add novelist writers.',
    },
    {
        'name': 'Books',
        'description': 'Manage and add novelist books.',
    },
    {
        'name': 'Auth',
        'description': "Manage all user's security.",
    },
]

app = FastAPI(
    title='MADR',
    openapi_tags=tags_metadata,
    swagger_ui_parameters={'defaultModelsExpandDepth': 0},
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == HTTPStatus.UNAUTHORIZED:
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': 'Não autorizado'},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail},
    )


app.include_router(accounts_router.router)
app.include_router(novelists_router.router)
app.include_router(books_router.router)
app.include_router(auth_router.router)


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
    include_in_schema=False,
)
def read_root():
    return {'message': 'MADR Online!'}
