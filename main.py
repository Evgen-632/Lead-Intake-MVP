import logging
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator

import database
import logging_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.init_db()
    except sqlite3.Error:
        logging_config.log_event(logging.ERROR, "Не удалось инициализировать SQLite", exc_info=True)
    yield


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)


class Lead(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: StrictStr = ""
    contact: StrictStr
    source: StrictStr = ""
    comment: StrictStr = ""

    @field_validator("contact")
    @classmethod
    def contact_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("Контакт не может быть пустым")
        return value


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Некорректный JSON или поля заявки. Проверьте контакт и типы полей."})


@app.post("/lead")
def create_lead(lead: Lead):
    try:
        lead_id = database.save_lead(lead.name, lead.contact, lead.source, lead.comment)
    except sqlite3.Error:
        logging_config.log_event(logging.ERROR, "Не удалось сохранить заявку в SQLite", exc_info=True)
        raise HTTPException(status_code=500, detail="Не удалось сохранить заявку. Попробуйте позже.")
    logging_config.log_event(logging.INFO, "New lead saved: %s", lead_id)
    return {"status": "ok", "lead_id": lead_id, "message": "Заявка успешно сохранена"}
