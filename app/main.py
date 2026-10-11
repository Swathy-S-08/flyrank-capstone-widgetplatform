from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import NotFoundError
from app.routes import widgets

app = FastAPI(title="Widget Platform")


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    fields = {
        ".".join(str(p) for p in e["loc"][1:]): e["msg"] for e in exc.errors()
    }
    return JSONResponse(
        status_code=400, content={"error": "Validation failed", "fields": fields}
    )


app.include_router(widgets.router)


@app.get("/health")
def health():
    return {"status": "ok"}
