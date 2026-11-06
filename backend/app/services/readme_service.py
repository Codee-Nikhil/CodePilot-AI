"""Generate a README.md for a repository from its file tree and key files."""
from app.ai import providers
from app.ai.llm import LLMMessage
from app.ai.readme_prompts import README_SYSTEM_PROMPT, build_readme_prompt
from app.core.exceptions import RepoNotFoundError
from app.models.readme import ReadmeDoc
from app.models.user import User
from app.repositories.file_repository import FileRepository
from app.repositories.readme_repository import ReadmeRepository
from app.repositories.repo_repository import RepoRepository

MAX_CHARS_PER_FILE = 6000
# Likely-important files to ground the README, if present in the repo
KEY_FILE_HINTS = (
    "readme", "package.json", "pyproject.toml", "requirements.txt", "setup.py",
    "main.py", "app.py", "index.js", "index.ts",
)


class ReadmeService:
    def __init__(self, readmes: ReadmeRepository, repos: RepoRepository, files: FileRepository) -> None:
        self.readmes = readmes
        self.repos = repos
        self.files = files

    def get_readme(self, user: User, repo_id: int) -> ReadmeDoc | None:
        repo = self.repos.get_for_user(user.id, repo_id)
        if repo is None:
            raise RepoNotFoundError()
        return self.readmes.get_for_repo(repo.id)

    def generate(self, user: User, repo_id: int) -> ReadmeDoc:
        repo = self.repos.get_for_user(user.id, repo_id)
        if repo is None:
            raise RepoNotFoundError()

        tree = [row.path for row in self.files.list_tree(repo.id)]
        key_paths = [p for p in tree if any(hint in p.lower() for hint in KEY_FILE_HINTS)][:8]
        files = self.files.get_many_by_paths(repo.id, key_paths)
        file_pairs = [(f.path, f.content[:MAX_CHARS_PER_FILE]) for f in files]

        prompt = build_readme_prompt(repo.full_name, repo.description, tree, file_pairs)
        content = providers.get_llm().complete(README_SYSTEM_PROMPT, [LLMMessage("user", prompt)])
        return self.readmes.upsert(repo.id, content.strip())
