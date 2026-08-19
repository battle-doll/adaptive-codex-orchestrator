#!/usr/bin/env python3
"""Validate a deterministic Adaptive Codex Orchestrator release archive.

The default validation path treats the archive as untrusted data: it parses,
decompresses, and syntax-checks files but never imports archive code.  The
builder may additionally supply a trusted source tree.  In that mode every
archive byte is first matched to the local source before a small isolated
import smoke test is allowed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import unicodedata
import zipfile


PACKAGE_NAME = "adaptive-codex-orchestrator"
PACKAGE_VERSION = "0.1.0"
ARCHIVE_NAME = f"{PACKAGE_NAME}-{PACKAGE_VERSION}.zip"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_MEMBER_BYTES = 5 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 20 * 1024 * 1024
MAX_MEMBERS = 1000
MAX_PATH_LENGTH = 512
MAX_COMPRESSION_RATIO = 200

CRITICAL_PATHS = frozenset(
    {
        ".codex-plugin/plugin.json",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "assets/composer-icon.png",
        "assets/logo.png",
        "evals/reviewer-cases.json",
        "hooks/hooks.json",
        "hooks/runtime.py",
        "hooks/run_runtime.sh",
        "hooks/run_runtime.ps1",
        "skills/adaptive-orchestration/SKILL.md",
        "skills/adaptive-orchestration/agents/openai.yaml",
        "skills/adaptive-orchestration/references/model-policy.json",
        "docs/ARCHITECTURE.md",
        "docs/COMPATIBILITY.md",
        "docs/PRIVACY.md",
        "docs/PUBLISHING.md",
        "docs/SECURITY.md",
        "docs/TERMS.md",
        "docs/TESTING.md",
        "scripts/build_release.py",
        "scripts/validate_release_artifact.py",
    }
)

_WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)
_GENERIC_USER_NAMES = frozenset(
    {
        "example",
        "sample",
        "test",
        "user",
        "username",
        "name",
        "public",
        "shared",
    }
)
_WINDOWS_USER_PATH_RE = re.compile(
    r"(?i)(?:[a-z]:[\\/]+users[\\/]+)([^\\/\r\n<>:$%{}]+)"
    r"(?=[\\/]|[\s\"'`)>,;\]]|$)"
)
_POSIX_USER_PATH_RE = re.compile(
    r"/(?:users|home)/([^/\r\n<>$%{}]+)(?=/|[\s\"'`)>,;\]]|$)", re.IGNORECASE
)


class ReleaseValidationError(ValueError):
    """Raised when an archive violates the release contract."""


class DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: Sequence[Tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json(data: bytes, label: str) -> object:
    try:
        text = data.decode("utf-8")
        return json.loads(text, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise ReleaseValidationError(f"invalid JSON in {label}: {exc}") from exc


def _portable_key(name: str) -> str:
    return unicodedata.normalize("NFKC", name).casefold()


def validate_member_name(name: str) -> str:
    """Return the plugin-relative path for one safe canonical ZIP member."""

    if not isinstance(name, str) or not name:
        raise ReleaseValidationError("ZIP member name must be a non-empty string")
    if len(name) > MAX_PATH_LENGTH:
        raise ReleaseValidationError(f"ZIP member path is too long: {name!r}")
    if name != unicodedata.normalize("NFC", name):
        raise ReleaseValidationError(f"ZIP member path is not NFC-normalized: {name!r}")
    if "\\" in name or name.startswith("/") or name.endswith("/") or "//" in name:
        raise ReleaseValidationError(f"unsafe ZIP member path: {name!r}")
    if "\x00" in name or any(ord(character) < 32 for character in name):
        raise ReleaseValidationError(f"control character in ZIP member path: {name!r}")

    path = PurePosixPath(name)
    parts = path.parts
    if not parts or parts[0] != PACKAGE_NAME or len(parts) < 2:
        raise ReleaseValidationError(
            f"ZIP member must be inside the single {PACKAGE_NAME!r} folder: {name!r}"
        )
    for part in parts:
        if part in {"", ".", ".."} or part.endswith((" ", ".")) or ":" in part:
            raise ReleaseValidationError(f"unsafe ZIP path segment {part!r} in {name!r}")
        if len(part) > 255:
            raise ReleaseValidationError(f"ZIP path segment is too long in {name!r}")
        stem = part.split(".", 1)[0].casefold()
        if stem in _WINDOWS_RESERVED:
            raise ReleaseValidationError(f"reserved Windows path segment in {name!r}")

    relative = PurePosixPath(*parts[1:]).as_posix()
    return relative


def is_secret_like_filename(relative_name: str) -> bool:
    """Detect credential/private-key filenames without rejecting SECURITY docs."""

    name = PurePosixPath(relative_name).name.casefold()
    exact = {
        ".env",
        ".npmrc",
        ".pypirc",
        "auth.json",
        "credentials.json",
        "secrets.json",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
    }
    if name in exact or name.startswith(".env."):
        return True
    if name.endswith((".pem", ".key", ".p12", ".pfx", ".jks", ".keystore")):
        return True
    return bool(
        re.search(
            r"(?:^|[-_.])(?:private[-_]?key|credentials?|secrets?|"
            r"api[-_]?key|access[-_]?token|auth[-_]?token)(?:[-_.]|$)",
            name,
        )
    )


def private_path_markers(data: bytes) -> Tuple[str, ...]:
    """Find machine-private user-home paths while allowing explicit test examples."""

    text = data.decode("utf-8", errors="ignore").replace("\\\\", "\\")
    findings: List[str] = []
    for match in _WINDOWS_USER_PATH_RE.finditer(text):
        user = match.group(1).strip().casefold()
        if user not in _GENERIC_USER_NAMES:
            findings.append(f"Windows user-home path for {match.group(1)!r}")
    for match in _POSIX_USER_PATH_RE.finditer(text):
        user = match.group(1).strip().casefold()
        if user not in _GENERIC_USER_NAMES:
            findings.append(f"POSIX user-home path for {match.group(1)!r}")
    root_home_pattern = r"(?<![A-Za-z0-9_])/" + "root" + "/"
    if re.search(root_home_pattern, text):
        findings.append("root user-home path")
    return tuple(sorted(set(findings)))


def _validate_sidecar(archive: Path, digest: str) -> None:
    sidecar = archive.with_name(archive.name + ".sha256")
    if not sidecar.exists():
        return
    if not sidecar.is_file() or sidecar.is_symlink():
        raise ReleaseValidationError("SHA-256 sidecar must be a regular file")
    try:
        value = sidecar.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as exc:
        raise ReleaseValidationError("SHA-256 sidecar is unreadable") from exc
    expected = f"{digest}  {archive.name}\n"
    if value != expected:
        raise ReleaseValidationError("SHA-256 sidecar content does not match the archive")


def _safe_extract(
    archive: zipfile.ZipFile, members: Sequence[zipfile.ZipInfo], destination: Path
) -> Path:
    for info in members:
        relative = validate_member_name(info.filename)
        target = destination / PACKAGE_NAME / Path(*PurePosixPath(relative).parts)
        resolved_parent = target.parent.resolve()
        root = (destination / PACKAGE_NAME).resolve()
        try:
            resolved_parent.relative_to(root)
        except ValueError as exc:
            raise ReleaseValidationError("archive extraction path escaped its root") from exc
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(info))
    return destination / PACKAGE_NAME


def _trusted_source_matches(
    archive: zipfile.ZipFile,
    members: Sequence[zipfile.ZipInfo],
    source_root: Path,
) -> None:
    root = source_root.resolve(strict=True)
    for info in members:
        relative = validate_member_name(info.filename)
        source = root.joinpath(*PurePosixPath(relative).parts)
        try:
            resolved = source.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError) as exc:
            raise ReleaseValidationError(
                f"trusted source is missing or escaping for {relative!r}"
            ) from exc
        if source.is_symlink() or not resolved.is_file():
            raise ReleaseValidationError(f"trusted source is not a regular file: {relative!r}")
        try:
            source_data = resolved.read_bytes()
        except OSError as exc:
            raise ReleaseValidationError(f"trusted source is unreadable: {relative!r}") from exc
        if source_data != archive.read(info):
            raise ReleaseValidationError(f"archive differs from trusted source: {relative!r}")


_SMOKE_SCRIPT = r"""
import importlib.util
from pathlib import Path
import sys

root = Path.cwd()
runtime_path = root / "hooks" / "runtime.py"
spec = importlib.util.spec_from_file_location("adaptive_release_runtime", runtime_path)
if spec is None or spec.loader is None:
    raise SystemExit("runtime import spec unavailable")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
decision = module.parse_command("Turn on Ultra Orchestration")
if decision.intent != "enable" or decision.scope != "session":
    raise SystemExit("parser smoke decision failed")
policy = module.load_model_policy(root)
if policy.get("primary_worker") != "gpt-5.3-codex-spark":
    raise SystemExit("model policy smoke validation failed")
""".strip()


def _trusted_smoke_import(extracted_root: Path) -> None:
    environment: Dict[str, str] = {}
    for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            environment[key] = value
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", _SMOKE_SCRIPT],
            cwd=str(extracted_root),
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReleaseValidationError("trusted archive smoke import could not run") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown failure").strip()[:500]
        raise ReleaseValidationError(f"trusted archive smoke import failed: {detail}")


def validate_archive(
    archive_path: Path,
    *,
    trusted_source_root: Optional[Path] = None,
    require_sidecar: bool = False,
) -> Mapping[str, object]:
    """Validate an archive and return deterministic summary facts."""

    archive_path = Path(archive_path)
    if archive_path.name != ARCHIVE_NAME:
        raise ReleaseValidationError(
            f"archive must be named {ARCHIVE_NAME!r}, got {archive_path.name!r}"
        )
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ReleaseValidationError("archive must be a regular file")
    archive_size = archive_path.stat().st_size
    if archive_size <= 0 or archive_size > MAX_ARCHIVE_BYTES:
        raise ReleaseValidationError("archive size is empty or exceeds the release limit")

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if require_sidecar and not archive_path.with_name(archive_path.name + ".sha256").is_file():
        raise ReleaseValidationError("required SHA-256 sidecar is missing")
    _validate_sidecar(archive_path, digest)

    try:
        archive = zipfile.ZipFile(archive_path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReleaseValidationError("release is not a readable ZIP archive") from exc

    with archive:
        if archive.comment:
            raise ReleaseValidationError("ZIP archive comment must be empty")
        members = archive.infolist()
        if not members or len(members) > MAX_MEMBERS:
            raise ReleaseValidationError("ZIP member count is empty or exceeds the limit")
        member_names = [info.filename for info in members]
        if member_names != sorted(member_names):
            raise ReleaseValidationError("ZIP members are not in deterministic sorted order")

        exact_names: set = set()
        portable_names: Dict[str, str] = {}
        relative_names: set = set()
        total_size = 0
        for info in members:
            if info.is_dir():
                raise ReleaseValidationError("release ZIP must contain file entries only")
            relative = validate_member_name(info.filename)
            if info.filename in exact_names:
                raise ReleaseValidationError(f"duplicate ZIP member: {info.filename!r}")
            exact_names.add(info.filename)
            key = _portable_key(info.filename)
            previous = portable_names.get(key)
            if previous is not None:
                raise ReleaseValidationError(
                    f"portable path collision: {previous!r} and {info.filename!r}"
                )
            portable_names[key] = info.filename
            relative_names.add(relative)

            if is_secret_like_filename(relative):
                raise ReleaseValidationError(f"secret-like filename in archive: {relative!r}")
            if info.date_time != FIXED_ZIP_TIMESTAMP:
                raise ReleaseValidationError(f"non-deterministic ZIP timestamp: {info.filename!r}")
            if info.create_system != 3:
                raise ReleaseValidationError(f"ZIP member lacks fixed Unix metadata: {info.filename!r}")
            if info.extra or info.comment:
                raise ReleaseValidationError(f"ZIP member has non-deterministic extra data: {info.filename!r}")
            if info.flag_bits & 0x1:
                raise ReleaseValidationError(f"encrypted ZIP member is forbidden: {info.filename!r}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise ReleaseValidationError(f"unexpected ZIP compression type: {info.filename!r}")
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_IFMT(unix_mode) == stat.S_IFLNK:
                raise ReleaseValidationError(f"symlink ZIP member is forbidden: {info.filename!r}")
            expected_permissions = 0o755 if relative.endswith(".sh") else 0o644
            expected_mode = stat.S_IFREG | expected_permissions
            if unix_mode != expected_mode:
                raise ReleaseValidationError(f"ZIP member mode is not deterministic: {info.filename!r}")
            if info.file_size > MAX_MEMBER_BYTES:
                raise ReleaseValidationError(f"ZIP member exceeds the size limit: {info.filename!r}")
            total_size += info.file_size
            if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise ReleaseValidationError("ZIP total uncompressed size exceeds the limit")
            if info.file_size >= 64 * 1024:
                ratio = info.file_size / max(info.compress_size, 1)
                if ratio > MAX_COMPRESSION_RATIO:
                    raise ReleaseValidationError(f"suspicious compression ratio: {info.filename!r}")

            data = archive.read(info)
            markers = private_path_markers(data)
            if markers:
                raise ReleaseValidationError(
                    f"private absolute path in {relative!r}: {', '.join(markers)}"
                )
            if relative.endswith(".py"):
                try:
                    compile(data, info.filename, "exec", dont_inherit=True)
                except (SyntaxError, ValueError, TypeError) as exc:
                    raise ReleaseValidationError(f"Python syntax failure in {relative!r}: {exc}") from exc

        missing = sorted(CRITICAL_PATHS - relative_names)
        if missing:
            raise ReleaseValidationError(f"critical release paths are missing: {', '.join(missing)}")

        manifest_path = f"{PACKAGE_NAME}/.codex-plugin/plugin.json"
        manifest = _load_json(archive.read(manifest_path), ".codex-plugin/plugin.json")
        if not isinstance(manifest, Mapping):
            raise ReleaseValidationError("plugin manifest root must be an object")
        if manifest.get("name") != PACKAGE_NAME:
            raise ReleaseValidationError("plugin manifest name does not match the release")
        if manifest.get("version") != PACKAGE_VERSION:
            raise ReleaseValidationError("plugin manifest version does not match the release")

        for critical_json in (
            "hooks/hooks.json",
            "skills/adaptive-orchestration/references/model-policy.json",
        ):
            _load_json(archive.read(f"{PACKAGE_NAME}/{critical_json}"), critical_json)

        corrupt = archive.testzip()
        if corrupt is not None:
            raise ReleaseValidationError(f"ZIP CRC validation failed for {corrupt!r}")

        if trusted_source_root is not None:
            _trusted_source_matches(archive, members, Path(trusted_source_root))
            with tempfile.TemporaryDirectory(prefix="adaptive-release-smoke-") as temporary:
                extracted = _safe_extract(archive, members, Path(temporary))
                _trusted_smoke_import(extracted)

    return {
        "archive": str(archive_path.resolve()),
        "sha256": digest,
        "file_count": len(members),
        "compressed_bytes": archive_size,
        "uncompressed_bytes": total_size,
        "trusted_smoke_import": trusted_source_root is not None,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help=f"Path to {ARCHIVE_NAME}")
    parser.add_argument(
        "--trusted-source-root",
        type=Path,
        help="Enable byte-for-byte source comparison and isolated smoke import",
    )
    parser.add_argument(
        "--require-sidecar",
        action="store_true",
        help="Require and validate <archive>.sha256",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_archive(
            args.archive,
            trusted_source_root=args.trusted_source_root,
            require_sidecar=args.require_sidecar,
        )
    except (OSError, ReleaseValidationError, zipfile.BadZipFile) as exc:
        print(f"Release artifact validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
