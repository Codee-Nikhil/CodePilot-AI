import pytest

from app.utils.repo_files import detect_language, should_skip


@pytest.mark.parametrize("path, expected", [("a/b.py", "python"), ("Dockerfile", "dockerfile"), ("x.TSX", "tsx"), ("notes.txt", None)])
def test_detect_language(path, expected):
    assert detect_language(path) == expected


@pytest.mark.parametrize("path", [
    "node_modules/x/index.js", "a/.git/config", "app.min.js", "yarn.lock", "img/logo.svg", ".env", "api/.env.local",
])
def test_skips_junk_and_secrets(path):
    assert should_skip(path)


@pytest.mark.parametrize("path", ["src/main.py", "README.md", "docs/build-guide.md", ".env.example"])
def test_keeps_real_files(path):
    assert not should_skip(path)
