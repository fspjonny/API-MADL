from pydantic import BaseModel


class MessageSchema(BaseModel):
    message: str


class ErrorDetailSchema(BaseModel):
    detail: str
