"""Maps domain errors raised in services to HTTP responses, in one place."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core import exceptions as errors

STATUS_BY_ERROR: dict[type[errors.DomainError], int] = {
    errors.EmailAlreadyRegisteredError: 409,
    errors.InvalidCredentialsError: 401,
    errors.GitHubNotConfiguredError: 503,
    errors.GitHubNotConnectedError: 409,
    errors.GitHubAuthError: 409,
    errors.GitHubAccountInUseError: 409,
    errors.GitHubNotFoundError: 404,
    errors.GitHubAPIError: 502,
    errors.InvalidStateError: 400,
    errors.RepoAlreadyImportedError: 409,
    errors.RepoNotFoundError: 404,
    errors.RepoFileNotFoundError: 404,
    errors.RepoTooLargeError: 413,
    errors.LLMNotConfiguredError: 503,
    errors.LLMError: 502,
    errors.EmbeddingError: 502,
    errors.RepoNotIndexedError: 409,
    errors.RepoIndexingError: 409,
    errors.ChatNotFoundError: 404,
    errors.ReviewNotFoundError: 404,
    errors.ReviewInProgressError: 409,
    errors.ReviewFailedError: 502,
    errors.ReadmeNotFoundError: 404,
    errors.WrongPasswordError: 401,
}


def _handler_for(status_code: int):
    async def handler(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"detail": str(error)})

    return handler


def register_exception_handlers(app: FastAPI) -> None:
    for error_type, status_code in STATUS_BY_ERROR.items():
        app.add_exception_handler(error_type, _handler_for(status_code))
