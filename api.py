import sys
from fastapi import FastAPI
from routes import tags, static
from db.common import init_db
from contextlib import asynccontextmanager
from toolbox.api import logger_middleware, init_scalar_docs, run_server
from toolbox.utils import get_env


ENV = get_env("ENV", "PROD", verbose=1)
HOT_RELOAD = False if ENV == "PROD" else get_env("HOT_RELOAD", False, verbose=1)
LOG_REQUESTS = get_env("LOG_REQUESTS", False, verbose=1)
LOG_RESPONSE = get_env("LOG_RESPONSE", False, verbose=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=f"[{ENV}] NHaiku",
    version="🌸",
    docs_url=None,
    lifespan=lifespan,
)

app.include_router(tags.router)
app.include_router(static.router)


if ENV == "DEV" or LOG_REQUESTS or LOG_RESPONSE:
    logger_middleware(app, ENV, LOG_REQUESTS, LOG_RESPONSE)


init_scalar_docs(
    app,
    title=f"[{ENV}] NHaiku API Doc",
    favicon_url="/favicon.ico",
    authentication={"preferredSecurityScheme": "ApiKeyAuth"},
    persist_auth=True,
)


sys.stdout.reconfigure(line_buffering=True)


if __name__ == "__main__":
    run_server("api:app", ENV, port=8069, hot_reload=HOT_RELOAD)
