"""Thin wrapper over GitHub's OAuth and REST APIs. The only module that talks to GitHub."""
import io
from urllib.parse import quote, urlencode

import httpx

from app.core.config import get_settings
from app.core.exceptions import GitHubAPIError, GitHubAuthError, GitHubNotFoundError, RepoTooLargeError

API_URL = "https://api.github.com"
OAUTH_URL = "https://github.com/login/oauth"
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
TIMEOUT = 20.0
USER_AGENT = "CodePilot-AI"


class GitHubClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def authorize_url(self, state: str) -> str:
        query = urlencode({
            "client_id": self.settings.github_client_id,
            "redirect_uri": self.settings.github_redirect_uri,
            "scope": self.settings.github_oauth_scope,
            "state": state,
        })
        return f"{OAUTH_URL}/authorize?{query}"

    def exchange_code(self, code: str) -> str:
        try:
            res = httpx.post(
                f"{OAUTH_URL}/access_token",
                json={
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "code": code,
                    "redirect_uri": self.settings.github_redirect_uri,
                },
                headers={"Accept": "application/json", "User-Agent": USER_AGENT},
                timeout=TIMEOUT,
            )
            data = res.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GitHubAPIError("Could not reach GitHub") from exc
        token = data.get("access_token")
        if not token:
            raise GitHubAuthError()
        return token

    def revoke_token(self, token: str) -> None:
        try:
            httpx.request(
                "DELETE",
                f"{API_URL}/applications/{self.settings.github_client_id}/grant",
                auth=(self.settings.github_client_id, self.settings.github_client_secret),
                json={"access_token": token},
                headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
                timeout=TIMEOUT,
            )
        except httpx.HTTPError:
            pass

    def get_user(self, token: str) -> dict:
        return self._get("/user", token)

    def list_repos(self, token: str, max_pages: int = 3) -> list[dict]:
        repos: list[dict] = []
        for page in range(1, max_pages + 1):
            batch = self._get(
                "/user/repos", token, per_page=100, page=page, sort="updated",
                affiliation="owner,collaborator,organization_member",
            )
            repos.extend(batch)
            if len(batch) < 100:
                break
        return repos

    def get_repo(self, token: str, full_name: str) -> dict:
        return self._get(f"/repos/{full_name}", token)

    def get_repo_by_id(self, token: str, github_id: int) -> dict:
        return self._get(f"/repositories/{github_id}", token)

    def download_tarball(self, token: str, full_name: str, ref: str) -> io.BytesIO:
        buffer = io.BytesIO()
        url = f"{API_URL}/repos/{full_name}/tarball/{quote(ref, safe='/')}"
        try:
            with httpx.stream(
                "GET", url, headers=self._headers(token), follow_redirects=True, timeout=60.0
            ) as res:
                self._raise_for_status(res)
                for chunk in res.iter_bytes():
                    buffer.write(chunk)
                    if buffer.tell() > MAX_ARCHIVE_BYTES:
                        raise RepoTooLargeError()
        except httpx.HTTPError as exc:
            raise GitHubAPIError("Could not download the repository") from exc
        buffer.seek(0)
        return buffer

    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }

    def _get(self, path: str, token: str, **params):
        try:
            res = httpx.get(
                f"{API_URL}{path}", headers=self._headers(token), params=params or None,
                timeout=TIMEOUT, follow_redirects=True,
            )
        except httpx.HTTPError as exc:
            raise GitHubAPIError("Could not reach GitHub") from exc
        self._raise_for_status(res)
        return res.json()

    @staticmethod
    def _raise_for_status(res: httpx.Response) -> None:
        if res.status_code == 401:
            raise GitHubAuthError()
        if res.status_code == 404:
            raise GitHubNotFoundError()
        if res.status_code == 403 and res.headers.get("x-ratelimit-remaining") == "0":
            raise GitHubAPIError("GitHub rate limit reached. Try again later")
        if res.status_code >= 400:
            raise GitHubAPIError(f"GitHub returned an error ({res.status_code})")
