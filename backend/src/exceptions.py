from fastapi import status, FastAPI, Request, Response, HTTPException
from fastapi.exception_handlers import http_exception_handler

from .core.exceptions import NotFoundError, BadRequestError, UnauthorizedError


async def not_found_error_handler(request: Request, exc: NotFoundError) -> Response:
    return await http_exception_handler(request, HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message))


async def bad_request_error_handler(request: Request, exc: BadRequestError) -> Response:
    return await http_exception_handler(request, HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message))


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> Response:
    return await http_exception_handler(request, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message))



def apply_exception_handlers(app: FastAPI):
    app.exception_handler(NotFoundError)(not_found_error_handler)
    app.exception_handler(BadRequestError)(bad_request_error_handler)
    app.exception_handler(UnauthorizedError)(unauthorized_error_handler)
    return app