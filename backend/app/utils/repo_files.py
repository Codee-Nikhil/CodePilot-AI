"""Filtering, language detection and extraction of files from a GitHub tarball."""
import hashlib
import tarfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import BinaryIO

MAX_FILE_BYTES = 200_000
MAX_FILES = 500
MAX_TOTAL_BYTES = 20_000_000
MAX_PATH_LENGTH = 1024

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", "venv", ".venv", "__pycache__",
    "vendor", "target", ".idea", ".vscode", "coverage", ".pytest_cache", ".mypy_cache",
}
SKIP_FILENAMES = {"package-lock.json", "pnpm-lock.yaml", ".DS_Store"}
SKIP_SUFFIXES = (".min.js", ".min.css", ".map", ".lock", ".svg")
ENV_ALLOWED = {".env.example", ".env.sample"}

LANGUAGE_BY_EXTENSION = {
    ".py": "python", ".js": "javascript", ".jsx": "jsx", ".ts": "typescript", ".tsx": "tsx",
    ".java": "java", ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".cs": "csharp",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift",
    ".kt": "kotlin", ".sql": "sql", ".sh": "bash", ".json": "json", ".yml": "yaml",
    ".yaml": "yaml", ".toml": "toml", ".md": "markdown", ".html": "html", ".css": "css",
    ".scss": "scss",
}
LANGUAGE_BY_FILENAME = {"Dockerfile": "dockerfile", "Makefile": "makefile"}


@dataclass(frozen=True)
class ParsedFile:
    path: str
    content: str
    size: int
    language: str | None
    content_hash: str


@dataclass(frozen=True)
class SyncCounts:
    added: int
    updated: int
    removed: int


def detect_language(path: str) -> str | None:
    p = PurePosixPath(path)
    return LANGUAGE_BY_FILENAME.get(p.name) or LANGUAGE_BY_EXTENSION.get(p.suffix.lower())


def should_skip(path: str) -> bool:
    if len(path) > MAX_PATH_LENGTH:
        return True
    p = PurePosixPath(path)
    if any(part in SKIP_DIRS for part in p.parts[:-1]):
        return True
    if p.name.startswith(".env") and p.name not in ENV_ALLOWED:
        return True
    return p.name in SKIP_FILENAMES or p.name.lower().endswith(SKIP_SUFFIXES)


def _decode_text(data: bytes) -> str | None:
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def extract_text_files(archive: BinaryIO) -> dict[str, ParsedFile]:
    files: dict[str, ParsedFile] = {}
    total = 0
    with tarfile.open(fileobj=archive, mode="r:gz") as tar:
        for member in tar:
            if not member.isfile() or member.size > MAX_FILE_BYTES:
                continue
            _, _, path = member.name.partition("/")
            if not path or should_skip(path):
                continue
            handle = tar.extractfile(member)
            text = _decode_text(handle.read()) if handle else None
            if text is None:
                continue
            total += member.size
            files[path] = ParsedFile(
                path=path, content=text, size=member.size,
                language=detect_language(path), content_hash=hashlib.sha256(text.encode()).hexdigest(),
            )
            if len(files) >= MAX_FILES or total >= MAX_TOTAL_BYTES:
                break
    return files
