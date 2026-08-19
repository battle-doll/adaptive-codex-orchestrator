"""Privacy-preserving project identity without persisting a raw path."""

from __future__ import annotations

import hashlib
import ntpath
import os
from pathlib import Path
import posixpath
import subprocess
from typing import Callable, Optional, Sequence


def discover_repository_root(
    cwd: str,
    *,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    timeout: float = 1.5,
) -> str:
    """Return a Git root when safely available, otherwise the supplied CWD."""

    fallback = cwd or os.curdir
    try:
        result = runner(
            ["git", "-C", fallback, "rev-parse", "--show-toplevel"],
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return fallback
    if result.returncode == 0 and isinstance(result.stdout, str) and result.stdout.strip():
        return result.stdout.strip()
    return fallback


def normalize_path(value: str, *, platform: Optional[str] = None) -> str:
    """Normalize Windows/POSIX forms deterministically without filesystem access."""

    platform = platform or ("windows" if os.name == "nt" else "posix")
    if platform == "windows":
        normalized = ntpath.normpath(value.replace("/", "\\"))
        normalized = ntpath.normcase(normalized)
        # Hash representation uses one separator across hosts and removes the
        # non-semantic trailing separator except for a drive root.
        normalized = normalized.replace("\\", "/")
        if len(normalized) > 3:
            normalized = normalized.rstrip("/")
        return normalized
    normalized = posixpath.normpath(value.replace("\\", "/"))
    if normalized != "/":
        normalized = normalized.rstrip("/")
    return normalized


def project_id(
    cwd: str,
    *,
    platform: Optional[str] = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    timeout: float = 1.5,
) -> str:
    root = discover_repository_root(cwd, runner=runner, timeout=timeout)
    normalized = normalize_path(root, platform=platform)
    return hashlib.sha256(normalized.encode("utf-8", "surrogatepass")).hexdigest()


__all__ = ["discover_repository_root", "normalize_path", "project_id"]
