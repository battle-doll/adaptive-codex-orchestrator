#!/usr/bin/env python3
"""Build a deterministic full-plugin release ZIP and SHA-256 sidecar."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import unicodedata
import zipfile


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_release_artifact import (
    ARCHIVE_NAME,
    FIXED_ZIP_TIMESTAMP,
    MAX_MEMBER_BYTES,
    MAX_MEMBERS,
    MAX_TOTAL_UNCOMPRESSED_BYTES,
    PACKAGE_NAME,
    PACKAGE_VERSION,
    ReleaseValidationError,
    is_secret_like_filename,
    private_path_markers,
    validate_archive,
    validate_member_name,
)


EXCLUDED_DIRECTORIES = frozenset(
    {
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".cache",
        "htmlcov",
        "tmp",
        "temp",
        ".tmp",
    }
)
EXCLUDED_FILENAMES = frozenset(
    {".DS_Store", "Thumbs.db", ".coverage", "coverage.xml"}
)
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".tmp", ".swp", ".swo")


class ReleaseBuildError(RuntimeError):
    """Raised when source collection or reproducible output fails."""


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative: str
    size: int
    fingerprint: Tuple[int, int, int, int]


def _fingerprint(value: os.stat_result) -> Tuple[int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)


def _is_reparse(stat_value: os.stat_result) -> bool:
    attributes = getattr(stat_value, "st_file_attributes", 0)
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & marker)


def _check_not_link_or_reparse(path: Path, label: str) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise ReleaseBuildError(f"cannot inspect {label}: {path}") from exc
    if stat.S_ISLNK(value.st_mode) or _is_reparse(value):
        raise ReleaseBuildError(f"symlink or reparse point is forbidden for {label}: {path}")
    return value


def _excluded_file(name: str) -> bool:
    if name in EXCLUDED_FILENAMES or name.startswith(".coverage."):
        return True
    if name.endswith("~"):
        return True
    return name.casefold().endswith(EXCLUDED_SUFFIXES)


def _collect_sources(plugin_root: Path) -> List[SourceFile]:
    root_stat = _check_not_link_or_reparse(plugin_root, "plugin root")
    if not stat.S_ISDIR(root_stat.st_mode):
        raise ReleaseBuildError("plugin root must be a directory")
    root = plugin_root.resolve(strict=True)
    records: List[SourceFile] = []
    portable_paths: Dict[str, str] = {}
    total_size = 0

    def visit(directory: Path) -> None:
        nonlocal total_size
        try:
            entries = sorted(
                os.scandir(directory),
                key=lambda entry: unicodedata.normalize("NFC", entry.name),
            )
        except OSError as exc:
            raise ReleaseBuildError(f"cannot enumerate source directory: {directory}") from exc
        for entry in entries:
            path = Path(entry.path)
            value = _check_not_link_or_reparse(path, "source entry")
            try:
                relative_path = path.relative_to(root)
            except ValueError as exc:
                raise ReleaseBuildError(f"source path escaped plugin root: {path}") from exc
            relative = PurePosixPath(*relative_path.parts).as_posix()
            if relative != unicodedata.normalize("NFC", relative):
                raise ReleaseBuildError(f"source path is not NFC-normalized: {relative!r}")

            if stat.S_ISDIR(value.st_mode):
                if entry.name in EXCLUDED_DIRECTORIES:
                    continue
                visit(path)
                continue
            if not stat.S_ISREG(value.st_mode):
                raise ReleaseBuildError(f"special source file is forbidden: {relative!r}")
            if _excluded_file(entry.name):
                continue
            if is_secret_like_filename(relative):
                raise ReleaseBuildError(f"secret-like source filename is forbidden: {relative!r}")
            archive_name = f"{PACKAGE_NAME}/{relative}"
            try:
                validate_member_name(archive_name)
            except ReleaseValidationError as exc:
                raise ReleaseBuildError(str(exc)) from exc
            portable = unicodedata.normalize("NFKC", archive_name).casefold()
            previous = portable_paths.get(portable)
            if previous is not None:
                raise ReleaseBuildError(
                    f"portable source path collision: {previous!r} and {relative!r}"
                )
            portable_paths[portable] = relative
            if value.st_size > MAX_MEMBER_BYTES:
                raise ReleaseBuildError(f"source file exceeds size limit: {relative!r}")
            total_size += value.st_size
            if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise ReleaseBuildError("source tree exceeds total release size limit")
            records.append(
                SourceFile(
                    path=path,
                    relative=relative,
                    size=value.st_size,
                    fingerprint=_fingerprint(value),
                )
            )

    visit(root)
    if not records or len(records) > MAX_MEMBERS:
        raise ReleaseBuildError("source file count is empty or exceeds the release limit")
    records.sort(key=lambda item: f"{PACKAGE_NAME}/{item.relative}")
    return records


def _read_source(record: SourceFile, root: Path) -> bytes:
    try:
        before = record.path.lstat()
        resolved = record.path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ReleaseBuildError(f"source file became unavailable: {record.relative!r}") from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or _is_reparse(before)
        or not stat.S_ISREG(before.st_mode)
        or _fingerprint(before) != record.fingerprint
    ):
        raise ReleaseBuildError(f"source file changed before packaging: {record.relative!r}")

    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(str(record.path), flags)
    except OSError as exc:
        raise ReleaseBuildError(f"source file cannot be opened safely: {record.relative!r}") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or _fingerprint(opened) != record.fingerprint:
            raise ReleaseBuildError(f"source file changed while opening: {record.relative!r}")
        chunks: List[bytes] = []
        remaining = MAX_MEMBER_BYTES + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if len(data) != record.size or len(data) > MAX_MEMBER_BYTES:
        raise ReleaseBuildError(f"source size changed while reading: {record.relative!r}")
    if _fingerprint(after) != record.fingerprint:
        raise ReleaseBuildError(f"source file changed during packaging: {record.relative!r}")
    markers = private_path_markers(data)
    if markers:
        raise ReleaseBuildError(
            f"private absolute path in {record.relative!r}: {', '.join(markers)}"
        )
    return data


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=name, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    permissions = 0o755 if name.endswith(".sh") else 0o644
    info.external_attr = (stat.S_IFREG | permissions) << 16
    info.extra = b""
    info.comment = b""
    return info


def _build_once(target: Path, records: Sequence[SourceFile], root: Path) -> None:
    try:
        with zipfile.ZipFile(
            target,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            allowZip64=False,
        ) as archive:
            archive.comment = b""
            for record in records:
                name = f"{PACKAGE_NAME}/{record.relative}"
                archive.writestr(
                    _zip_info(name),
                    _read_source(record, root),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
    except (OSError, RuntimeError, ValueError, zipfile.LargeZipFile) as exc:
        if isinstance(exc, ReleaseBuildError):
            raise
        raise ReleaseBuildError(f"failed to build deterministic ZIP: {exc}") from exc


def _atomic_write(path: Path, data: bytes) -> None:
    descriptor: Optional[int] = None
    temporary: Optional[Path] = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if os.name != "nt":
            temporary.chmod(0o644)
        os.replace(temporary, path)
        temporary = None
        if os.name != "nt":
            directory_flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY
            directory_descriptor = os.open(str(path.parent), directory_flags)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    except OSError as exc:
        raise ReleaseBuildError(f"atomic write failed for {path.name!r}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def _load_and_check_manifest(root: Path) -> None:
    path = root / ".codex-plugin" / "plugin.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseBuildError("plugin manifest is missing or invalid") from exc
    if not isinstance(value, Mapping):
        raise ReleaseBuildError("plugin manifest root must be an object")
    if value.get("name") != PACKAGE_NAME or value.get("version") != PACKAGE_VERSION:
        raise ReleaseBuildError(
            f"manifest must declare {PACKAGE_NAME!r} version {PACKAGE_VERSION!r}"
        )


def _prepare_dist(root: Path) -> Path:
    dist = root / "dist"
    if dist.exists() or dist.is_symlink():
        value = _check_not_link_or_reparse(dist, "dist directory")
        if not stat.S_ISDIR(value.st_mode):
            raise ReleaseBuildError("dist exists but is not a directory")
    else:
        try:
            dist.mkdir(mode=0o755)
        except OSError as exc:
            raise ReleaseBuildError("could not create dist directory") from exc
        _check_not_link_or_reparse(dist, "dist directory")
    return dist


def build_release(plugin_root: Path) -> Mapping[str, object]:
    requested_root = Path(plugin_root)
    _check_not_link_or_reparse(requested_root, "plugin root")
    root = requested_root.resolve(strict=True)
    if root.name != PACKAGE_NAME:
        raise ReleaseBuildError(f"plugin root folder must be named {PACKAGE_NAME!r}")
    _load_and_check_manifest(root)
    records = _collect_sources(root)

    with tempfile.TemporaryDirectory(prefix="adaptive-release-build-") as temporary:
        work = Path(temporary)
        first = work / ARCHIVE_NAME
        second = work / ("second-" + ARCHIVE_NAME)
        _build_once(first, records, root)
        _build_once(second, records, root)
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        if first_bytes != second_bytes:
            raise ReleaseBuildError("two independent builds were not byte-identical")
        first_report = validate_archive(first, trusted_source_root=root)

        # The validator requires the canonical filename, so independently copy
        # the second build to a canonical validation location before checking it.
        second_canonical = work / "verification" / ARCHIVE_NAME
        second_canonical.parent.mkdir()
        second_canonical.write_bytes(second_bytes)
        second_report = validate_archive(second_canonical, trusted_source_root=root)
        if first_report["sha256"] != second_report["sha256"]:
            raise ReleaseBuildError("independent validation digests do not match")

        dist = _prepare_dist(root)
        archive_path = dist / ARCHIVE_NAME
        digest = str(first_report["sha256"])
        sidecar_path = dist / (ARCHIVE_NAME + ".sha256")
        sidecar = f"{digest}  {ARCHIVE_NAME}\n".encode("ascii")
        _atomic_write(archive_path, first_bytes)
        _atomic_write(sidecar_path, sidecar)

    final_report = dict(
        validate_archive(
            archive_path,
            trusted_source_root=root,
            require_sidecar=True,
        )
    )
    final_report["sidecar"] = str(sidecar_path.resolve())
    final_report["reproducible_builds"] = 2
    return final_report


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin-root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="Plugin root to package (defaults to the parent of this script directory)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = build_release(args.plugin_root)
    except (OSError, ReleaseBuildError, ReleaseValidationError) as exc:
        print(f"Release build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
