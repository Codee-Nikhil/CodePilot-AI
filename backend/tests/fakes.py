"""In-memory stand-ins for GitHub, the embedder, the vector store and the LLM.
Tests never touch the network or load real models."""
import io
import math
import re
import tarfile
import zlib

from app.ai.vector_store import Hit
from app.core.exceptions import EmbeddingError, GitHubAPIError, GitHubAuthError, GitHubNotFoundError, LLMError

REPO_INFO = {
    "id": 555, "name": "demo", "full_name": "octocat/demo", "description": "A demo repo",
    "language": "Python", "default_branch": "main", "html_url": "https://github.com/octocat/demo",
    "private": False, "stargazers_count": 3, "updated_at": "2026-01-01T00:00:00Z",
}

DEFAULT_FILES: dict[str, bytes] = {
    "README.md": b"# Demo\n",
    "src/main.py": b"print('hi')\n",
    "src/utils/helpers.py": b"def add(a, b):\n    return a + b\n",
    "node_modules/lib/index.js": b"module.exports = 1",
    "package-lock.json": b"{}",
    "poetry.lock": b"lock",
    ".env": b"SECRET=1",
    "logo.png": b"\x89PNG\r\n\x1a\n\x00\x00binary",
    "big.txt": b"x" * 300_000,
}


def make_tarball(files: dict[str, bytes]) -> io.BytesIO:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for path, data in files.items():
            info = tarfile.TarInfo(name=f"octocat-demo-abc123/{path}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    buf.seek(0)
    return buf


class FakeGitHub:
    def __init__(self) -> None:
        self.repo_info = dict(REPO_INFO)
        self.files = dict(DEFAULT_FILES)
        self.fail_download = False

    def authorize_url(self, state: str) -> str:
        return f"https://github.test/authorize?state={state}"

    def exchange_code(self, code: str) -> str:
        if code != "good":
            raise GitHubAuthError()
        return "gho_faketoken"

    def get_user(self, token: str) -> dict:
        return {"id": 1001, "login": "octocat"}

    def revoke_token(self, token: str) -> None:
        pass

    def list_repos(self, token: str) -> list[dict]:
        return [self.repo_info]

    def get_repo(self, token: str, full_name: str) -> dict:
        if full_name != self.repo_info["full_name"]:
            raise GitHubNotFoundError()
        return self.repo_info

    def get_repo_by_id(self, token: str, github_id: int) -> dict:
        if github_id != self.repo_info["id"]:
            raise GitHubNotFoundError()
        return self.repo_info

    def download_tarball(self, token: str, full_name: str, ref: str) -> io.BytesIO:
        if self.fail_download:
            raise GitHubAPIError("boom")
        return make_tarball(self.files)


class FakeEmbedder:
    DIM = 4096

    def __init__(self) -> None:
        self.name = "fake"
        self.embedded: list[str] = []
        self.fail = False

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for word in re.findall(r"\w+", text.lower()):
            vec[zlib.crc32(word.encode()) % self.DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self.fail:
            raise EmbeddingError("boom")
        self.embedded.extend(texts)
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


class FakeVectorStore:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def add(self, *, ids, embeddings, documents, metadatas) -> None:
        for id_, emb, doc, meta in zip(ids, embeddings, documents, metadatas):
            self.items[id_] = {"embedding": emb, "text": doc, **meta}

    def delete(self, ids) -> None:
        for id_ in ids:
            self.items.pop(id_, None)

    def delete_repo(self, repo_id: int) -> None:
        self.items = {k: v for k, v in self.items.items() if v["repo_id"] != repo_id}

    def query(self, repo_id: int, embedding, k: int) -> list[Hit]:
        scored = [
            (sum(a * b for a, b in zip(embedding, item["embedding"])), item)
            for item in self.items.values() if item["repo_id"] == repo_id
        ]
        scored.sort(key=lambda pair: -pair[0])
        return [
            Hit(path=i["path"], start_line=i["start_line"], end_line=i["end_line"], text=i["text"])
            for _, i in scored[:k]
        ]

    def count(self, repo_id: int) -> int:
        return sum(1 for v in self.items.values() if v["repo_id"] == repo_id)


DEFAULT_REVIEW_JSON = (
    '{"summary": "Mostly clean code with one bug.", "score": 80, "findings": '
    '[{"path": "src/main.py", "line": 1, "severity": "warning", "category": "style", '
    '"title": "Use a main guard", "description": "The print runs on import.", '
    '"suggestion": "Wrap in if __name__ == \\"__main__\\":"}]}'
)
DEFAULT_README_MD = "# demo\n\nA demo repository.\n\n## Getting Started\n\n```bash\npython src/main.py\n```\n"


class FakeLLM:
    """complete_reply is returned by complete() (review/README); reply is streamed by stream() (chat)."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.reply = "The add helper sums two numbers [src/utils/helpers.py:1-3]."
        self.complete_reply = DEFAULT_REVIEW_JSON
        self.fail = False

    def stream(self, system, messages):
        self.calls.append((system, messages))
        if self.fail:
            raise LLMError("boom")
        for word in self.reply.split(" "):
            yield word + " "

    def complete(self, system, messages) -> str:
        self.calls.append((system, messages))
        if self.fail:
            raise LLMError("boom")
        return self.complete_reply
