from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import NotFoundError, ValidationFailed
from app.routes import submissions, widgets

MAX_SUBMISSION_BYTES = 10_000

app = FastAPI(title="Widget Platform")


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(ValidationFailed)
async def validation_failed_handler(request: Request, exc: ValidationFailed):
    return JSONResponse(
        status_code=400, content={"error": "Validation failed", "fields": exc.fields}
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    fields = {
        ".".join(str(p) for p in e["loc"][1:]): e["msg"] for e in exc.errors()
    }
    return JSONResponse(
        status_code=400, content={"error": "Validation failed", "fields": fields}
    )


@app.middleware("http")
async def limit_submission_size(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/submissions":
        length = request.headers.get("content-length")
        if length is None:
            return JSONResponse(
                status_code=411, content={"error": "Content-Length required"}
            )
        if not length.isdigit():
            return JSONResponse(
                status_code=400, content={"error": "Invalid Content-Length"}
            )
        if int(length) > MAX_SUBMISSION_BYTES:
            return JSONResponse(
                status_code=413, content={"error": "Payload too large"}
            )
    return await call_next(request)


# Added last so it is the outermost layer: every response gets CORS headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)

app.include_router(widgets.router)
app.include_router(submissions.router)


@app.get("/health")
def health():
    return {"status": "ok"}
