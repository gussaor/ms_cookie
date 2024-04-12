import sentry_sdk
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from dependencies.fastapi_simple_security.endpoints import api_key_router
from api.errors.http_error import http_error_handler
from api.errors.validation_error import http422_error_handler
from api.router import router as api_router
from core.config import EnvironmentEnum, settings

if settings.environment != EnvironmentEnum.local.value:
    sentry_sdk.init(
        dsn="https://bed480300c814a85ab26dca4054bd2c8@o1342531.ingest.sentry.io/6623065",
        traces_sample_rate=0.25,
        profiles_sample_rate=0.25,
        environment=settings.environment.value,
    )


def get_application() -> FastAPI:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]

    application = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        openapi_prefix=settings.openapi_prefix,
        middleware=middleware,
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=settings.api_prefix)
    application.include_router(api_key_router, prefix="/auth", tags=["_auth"])

    return application


app = get_application()


@app.get("/")
def home():
    return {"Service": "{{cookiecutter.project_name}}"}