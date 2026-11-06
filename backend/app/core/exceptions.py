"""Domain errors raised by services; api/error_handlers.py maps them to HTTP responses."""


class DomainError(Exception):
    default_message = "Request failed"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class EmailAlreadyRegisteredError(DomainError):
    default_message = "Email already registered"


class InvalidCredentialsError(DomainError):
    default_message = "Incorrect email or password"


class GitHubNotConfiguredError(DomainError):
    default_message = "GitHub integration is not configured on the server"


class GitHubNotConnectedError(DomainError):
    default_message = "Connect your GitHub account first"


class GitHubAuthError(DomainError):
    default_message = "GitHub connection is invalid. Please reconnect"


class GitHubAccountInUseError(DomainError):
    default_message = "This GitHub account is linked to another user"


class GitHubNotFoundError(DomainError):
    default_message = "Repository not found or not accessible"


class GitHubAPIError(DomainError):
    default_message = "GitHub request failed"


class InvalidStateError(DomainError):
    default_message = "Invalid or expired OAuth state"


class RepoAlreadyImportedError(DomainError):
    default_message = "Repository already imported"


class RepoNotFoundError(DomainError):
    default_message = "Repository not found"


class RepoFileNotFoundError(DomainError):
    default_message = "File not found"


class RepoTooLargeError(DomainError):
    default_message = "Repository is too large to import"


class LLMNotConfiguredError(DomainError):
    default_message = "AI provider is not configured on the server"


class LLMError(DomainError):
    default_message = "The AI provider request failed"


class EmbeddingError(DomainError):
    default_message = "Embedding request failed"


class RepoNotIndexedError(DomainError):
    default_message = "Repository is not indexed yet"


class RepoIndexingError(DomainError):
    default_message = "Repository is already being indexed"


class ChatNotFoundError(DomainError):
    default_message = "Chat not found"


class ReviewNotFoundError(DomainError):
    default_message = "Review not found"


class ReviewInProgressError(DomainError):
    default_message = "A review is already running for this repository"


class ReviewFailedError(DomainError):
    default_message = "The AI review could not be completed"


class ReadmeNotFoundError(DomainError):
    default_message = "README not found"


class WrongPasswordError(DomainError):
    default_message = "Current password is incorrect"
