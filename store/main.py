from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from store.core.config import settings
from store.core.exceptions import BaseException
from store.routers import api_router

class App(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            version="0.0.1",
            title=settings.PROJECT_NAME,
            root_path=settings.ROOT_PATH
        )

app = App()

@app.exception_handler(BaseException)
async def handle_base_exc(request: Request, exc: BaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )

app.include_router(api_router)
