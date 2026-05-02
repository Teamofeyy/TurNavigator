from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache
def load_env_files() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    repo_root = backend_dir.parent
    candidate_files = [
        backend_dir / ".env.local",
        backend_dir / ".env",
        repo_root / ".env.local",
        repo_root / ".env",
    ]

    for candidate in candidate_files:
        if candidate.is_file():
            _load_env_file(candidate)


def _load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = key.strip()
        if not normalized_key:
            continue
        normalized_value = value.strip().strip('"').strip("'")
        if normalized_value or normalized_key not in os.environ:
            os.environ[normalized_key] = normalized_value
