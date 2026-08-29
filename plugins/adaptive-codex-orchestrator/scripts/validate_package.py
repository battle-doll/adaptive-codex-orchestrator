#!/usr/bin/env python3
"""Validate the Adaptive Codex Orchestrator package with the standard library."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
from typing import Any, Iterable, Mapping, Optional
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET


PLUGIN_NAME = "adaptive-codex-orchestrator"
SKILL_NAME = "adaptive-orchestration"
EXPECTED_STARTER_PROMPTS = (
    "Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.",
    "이번 작업만 울트라 오케스트레이션을 켜고 파서 버그를 재현한 뒤 최소 수정과 집중 테스트를 해줘.",
    "Show orchestration status, scope, and profile, and say whether persistent hooks are available.",
)
MANIFEST_ALLOWED_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
INTERFACE_ALLOWED_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "brandColor",
    "composerIcon",
    "logo",
    "logoDark",
    "screenshots",
    "defaultPrompt",
    "default_prompt",
}
REQUIRED_DOCUMENTS = {
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "docs/ARCHITECTURE.md",
    "docs/SECURITY.md",
    "docs/PRIVACY.md",
    "docs/TERMS.md",
    "docs/COMPATIBILITY.md",
    "docs/TESTING.md",
    "docs/PUBLISHING.md",
    "docs/VALIDATION.md",
}
ROOT_PUBLIC_DOCUMENTS = {
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh-CN.md",
    "README.ru.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "PRIVACY.md",
    "SECURITY.md",
    "SUBMISSION.md",
    "SUPPORT.md",
    "TERMS.md",
}
EXPECTED_I18N_DOCUMENTS = {
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh-CN.md",
    "README.ru.md",
    "PUBLISHING.ko.md",
    "PUBLISHING.ja.md",
    "PUBLISHING.zh-CN.md",
    "PUBLISHING.ru.md",
    *(f"{stem}{suffix}.md" for stem in ("SUPPORT", "SECURITY", "PRIVACY", "TERMS", "SUBMISSION") for suffix in ("", ".ko", ".ja", ".zh-CN", ".ru")),
}
REQUIRED_PACKAGE_FILES = {
    "pyproject.toml",
    "hooks/runtime.py",
    "hooks/run_runtime.sh",
    "hooks/run_runtime.ps1",
    "hooks/lib/__init__.py",
    "hooks/lib/command_parser.py",
    "hooks/lib/state_store.py",
    "hooks/lib/project_identity.py",
    "hooks/lib/policy_loader.py",
    "hooks/lib/hook_output.py",
    "tests/test_command_parser.py",
    "tests/test_state_store.py",
    "tests/test_project_identity.py",
    "tests/test_hooks.py",
    "tests/fixtures/hooks/session_start.json",
    "tests/fixtures/hooks/user_prompt_submit.json",
    "tests/fixtures/hooks/subagent_start.json",
    "tests/fixtures/hooks/stop.json",
    "tests/fixtures/hooks/session_end.json",
    "evals/prompts.jsonl",
    "evals/reviewer-cases.json",
    "evals/README.md",
    "scripts/evaluate_policies.py",
    "scripts/validate_package.py",
    "scripts/build_release.py",
    "scripts/validate_release_artifact.py",
}
REQUIRED_REFERENCES = {
    "command-language.md",
    "model-policy.json",
    "routing-policy.md",
    "runtime-policy.md",
    "worker-contracts.md",
}
EXPECTED_HOOK_EVENTS = {
    "SessionStart",
    "UserPromptSubmit",
    "SubagentStart",
    "Stop",
    "SessionEnd",
}
KNOWN_HOOK_EVENTS = EXPECTED_HOOK_EVENTS | {
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "PreCompact",
    "PostCompact",
    "SubagentStop",
}
FORBIDDEN_NETWORK_MODULES = {
    "aiohttp",
    "ftplib",
    "http",
    "httpx",
    "requests",
    "smtplib",
    "socket",
    "telnetlib",
    "urllib",
    "websockets",
}
ALLOWED_RUNTIME_IMPORTS = {
    "__future__",
    "contextlib",
    "copy",
    "dataclasses",
    "fcntl",
    "hashlib",
    "json",
    "lib",
    "msvcrt",
    "ntpath",
    "os",
    "pathlib",
    "posixpath",
    "re",
    "stat",
    "subprocess",
    "sys",
    "tempfile",
    "time",
    "typing",
    "unicodedata",
}
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")
WINDOWS_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]")
USER_POSIX_ABSOLUTE_RE = re.compile(r"/(?:Users|home|root)/")
NETWORK_URL_RE = re.compile(r"\b(?:https?|wss?)://", re.IGNORECASE)
SENSITIVE_NAME_RE = re.compile(
    r"(?:^|_)(?:prompt|transcript|source_code|repository_path|absolute_path|raw_input)(?:$|_)",
    re.IGNORECASE,
)


class DuplicateKeyError(ValueError):
    """Raised when JSON repeats a key."""


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.assertions = 0

    def check(self, condition: bool, message: str) -> bool:
        self.assertions += 1
        if not condition:
            self.errors.append(message)
            return False
        return True

    def require_file(self, path: Path, label: str) -> bool:
        return self.check(path.is_file(), f"missing {label}: {path}")


def _unique_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def load_json(path: Path, validator: Validator, label: str) -> Optional[dict[str, Any]]:
    if not validator.require_file(path, label):
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        validator.check(False, f"invalid {label}: {exc}")
        return None
    if not validator.check(isinstance(value, dict), f"{label} must contain a JSON object"):
        return None
    return value


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: object, *, non_empty: bool = False) -> bool:
    return isinstance(value, list) and (bool(value) or not non_empty) and all(
        _non_empty_string(item) for item in value
    )


def _contains_todo(value: object) -> bool:
    if isinstance(value, str):
        return "[TODO:" in value
    if isinstance(value, list):
        return any(_contains_todo(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_todo(item) for item in value.values())
    return False


def _https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def resolve_archive_file(base: Path, archive_root: Path, raw: object) -> Optional[Path]:
    if not _non_empty_string(raw):
        return None
    candidate = PurePosixPath(str(raw).replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (base / candidate.as_posix()).resolve()
    try:
        resolved.relative_to(archive_root.resolve())
    except ValueError:
        return None
    return resolved


def validate_manifest(plugin_root: Path, validator: Validator) -> Optional[dict[str, Any]]:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(path, validator, "plugin manifest")
    if manifest is None:
        return None

    unknown = sorted(set(manifest) - MANIFEST_ALLOWED_FIELDS)
    validator.check(not unknown, f"plugin manifest has unsupported fields: {', '.join(unknown)}")
    validator.check("hooks" not in manifest, "plugin manifest must omit unsupported hooks field")
    validator.check(manifest.get("name") == PLUGIN_NAME, f"plugin name must be {PLUGIN_NAME!r}")
    version = manifest.get("version")
    validator.check(
        isinstance(version, str) and SEMVER_RE.fullmatch(version) is not None,
        "plugin version must be strict semver",
    )
    validator.check(_non_empty_string(manifest.get("description")), "plugin description is required")
    validator.check(not _contains_todo(manifest), "plugin manifest contains an unfinished TODO marker")
    validator.check(manifest.get("skills") in {"skills", "./skills/", "./skills"}, "skills path must resolve to skills")

    author = manifest.get("author")
    validator.check(isinstance(author, dict), "plugin author must be an object")
    if isinstance(author, dict):
        validator.check(not (set(author) - {"name", "email", "url"}), "plugin author has unsupported fields")
        validator.check(_non_empty_string(author.get("name")), "plugin author.name is required")
        if "url" in author:
            validator.check(_https_url(author["url"]), "plugin author.url must be an absolute https URL")

    interface = manifest.get("interface")
    validator.check(isinstance(interface, dict), "plugin interface must be an object")
    if isinstance(interface, dict):
        unknown_interface = sorted(set(interface) - INTERFACE_ALLOWED_FIELDS)
        validator.check(
            not unknown_interface,
            f"plugin interface has unsupported fields: {', '.join(unknown_interface)}",
        )
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            validator.check(_non_empty_string(interface.get(key)), f"plugin interface.{key} is required")
        validator.check(
            isinstance(interface.get("displayName"), str)
            and len(interface["displayName"]) <= 30,
            "plugin display name must be at most 30 characters",
        )
        validator.check(
            isinstance(interface.get("shortDescription"), str)
            and len(interface["shortDescription"]) <= 30,
            "plugin short description must be at most 30 characters",
        )
        validator.check(
            interface.get("developerName") == "battle-doll",
            "plugin developerName must match the verified publisher battle-doll",
        )
        validator.check(
            _string_list(interface.get("capabilities")),
            "plugin interface.capabilities must be an array of strings",
        )
        prompts = interface.get("defaultPrompt", interface.get("default_prompt"))
        validator.check(
            isinstance(prompts, list) and 1 <= len(prompts) <= 3,
            "plugin starter prompts must contain one to three entries",
        )
        if isinstance(prompts, list):
            for index, prompt in enumerate(prompts):
                validator.check(
                    _non_empty_string(prompt) and len(prompt) <= 128,
                    f"plugin starter prompt {index} must be non-empty and at most 128 characters",
                )
            validator.check(
                tuple(prompts) == EXPECTED_STARTER_PROMPTS,
                "plugin starter prompts must match the reviewed public listing",
            )
        if "brandColor" in interface:
            validator.check(
                isinstance(interface["brandColor"], str)
                and HEX_COLOR_RE.fullmatch(interface["brandColor"]) is not None,
                "plugin interface.brandColor must use #RRGGBB",
            )
        for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            validator.check(
                _https_url(interface.get(key)),
                f"plugin interface.{key} must be an absolute https URL",
            )
        validator.check(
            interface.get("websiteURL")
            == "https://github.com/battle-doll/adaptive-codex-orchestrator",
            "plugin websiteURL must match the public repository",
        )
        validator.check(
            interface.get("privacyPolicyURL")
            == "https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md",
            "plugin privacyPolicyURL must match the root public policy",
        )
        validator.check(
            interface.get("termsOfServiceURL")
            == "https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md",
            "plugin termsOfServiceURL must match the root public terms",
        )
        for key in ("composerIcon", "logo", "logoDark"):
            if key in interface:
                asset = resolve_archive_file(plugin_root, plugin_root, interface[key])
                validator.check(asset is not None and asset.is_file(), f"plugin interface.{key} points to a missing or unsafe asset")
        validator.check(
            interface.get("composerIcon") == "./assets/composer-icon.png",
            "plugin composer icon must use the exact 48x48 PNG",
        )
        validator.check(
            interface.get("logo") == "./assets/logo.png",
            "plugin directory logo must use the exact 256x256 PNG",
        )
        screenshots = interface.get("screenshots", [])
        validator.check(isinstance(screenshots, list), "plugin interface.screenshots must be an array")
        if isinstance(screenshots, list):
            for index, screenshot in enumerate(screenshots):
                asset = resolve_archive_file(plugin_root, plugin_root, screenshot)
                validator.check(
                    asset is not None and asset.is_file() and asset.suffix.lower() == ".png",
                    f"plugin screenshot {index} must be an existing PNG inside the package",
                )

    for key in ("homepage", "repository"):
        validator.check(
            _https_url(manifest.get(key)),
            f"plugin {key} must be an absolute https URL",
        )
    validator.check(
        manifest.get("homepage")
        == "https://github.com/battle-doll/adaptive-codex-orchestrator",
        "plugin homepage must match the public repository",
    )
    validator.check(
        manifest.get("repository")
        == "https://github.com/battle-doll/adaptive-codex-orchestrator",
        "plugin repository must match the public repository",
    )
    if isinstance(author, dict):
        validator.check(
            author.get("name") == "battle-doll",
            "plugin author.name must match the verified publisher battle-doll",
        )
    validator.check(manifest.get("license") == "MIT", "plugin license metadata must be MIT")
    validator.check(_string_list(manifest.get("keywords"), non_empty=True), "plugin keywords must be a non-empty string array")
    validator.check("apps" not in manifest, "apps must be omitted when no .app.json companion exists")
    validator.check("mcpServers" not in manifest, "mcpServers must be omitted when no MCP companion exists")
    return manifest


def validate_marketplace(
    repo_root: Path,
    plugin_root: Path,
    manifest: Optional[Mapping[str, Any]],
    validator: Validator,
) -> None:
    path = repo_root / ".agents" / "plugins" / "marketplace.json"
    marketplace = load_json(path, validator, "marketplace manifest")
    if marketplace is None:
        return
    validator.check(
        marketplace.get("name") == PLUGIN_NAME,
        "public marketplace name must match the plugin name",
    )
    interface = marketplace.get("interface")
    validator.check(
        isinstance(interface, dict) and _non_empty_string(interface.get("displayName")),
        "marketplace interface.displayName is required",
    )
    if isinstance(interface, dict):
        validator.check(
            interface.get("displayName") == "Adaptive Codex Orchestrator",
            "marketplace display name must match the public listing",
        )
    plugins = marketplace.get("plugins")
    if not validator.check(isinstance(plugins, list), "marketplace plugins must be an array"):
        return
    names: list[str] = []
    matching: list[dict[str, Any]] = []
    for index, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            validator.check(False, f"marketplace plugin entry {index} must be an object")
            continue
        name = entry.get("name")
        if isinstance(name, str):
            names.append(name)
        if name == PLUGIN_NAME:
            matching.append(entry)
    validator.check(len(names) == len(set(names)), "marketplace plugin names must be unique")
    if not validator.check(len(matching) == 1, f"marketplace must contain exactly one {PLUGIN_NAME} entry"):
        return
    entry = matching[0]
    if manifest is not None:
        validator.check(entry.get("name") == manifest.get("name"), "marketplace and plugin names must match")
    source = entry.get("source")
    validator.check(
        isinstance(source, dict)
        and source.get("source") == "local"
        and source.get("path") == f"./plugins/{PLUGIN_NAME}",
        "marketplace source must be the canonical local plugin path",
    )
    validator.check(plugin_root == (repo_root / "plugins" / PLUGIN_NAME).resolve(), "plugin root must match marketplace source")
    policy = entry.get("policy")
    validator.check(isinstance(policy, dict), "marketplace policy must be an object")
    if isinstance(policy, dict):
        validator.check(
            policy.get("installation") in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"},
            "marketplace policy.installation is invalid",
        )
        validator.check(
            policy.get("authentication") in {"ON_INSTALL", "ON_USE"},
            "marketplace policy.authentication is invalid",
        )
        if "products" in policy:
            validator.check(_string_list(policy["products"], non_empty=True), "marketplace policy.products must be a string array")
    validator.check(_non_empty_string(entry.get("category")), "marketplace category is required")


def _parse_yaml_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return {}
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return ast.literal_eval(value)
    lowered = value.casefold()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_simple_yaml(text: str, validator: Validator, label: str) -> Optional[dict[str, Any]]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            validator.check(False, f"{label}:{line_number}: tabs are not allowed in indentation")
            return None
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if stripped.startswith("-") or ":" not in stripped:
            validator.check(False, f"{label}:{line_number}: unsupported YAML shape")
            return None
        key, raw_value = stripped.split(":", 1)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key) is None:
            validator.check(False, f"{label}:{line_number}: invalid YAML key {key!r}")
            return None
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            validator.check(False, f"{label}:{line_number}: invalid indentation")
            return None
        parent = stack[-1][1]
        if key in parent:
            validator.check(False, f"{label}:{line_number}: duplicate YAML key {key!r}")
            return None
        try:
            value = _parse_yaml_scalar(raw_value)
        except (ValueError, SyntaxError) as exc:
            validator.check(False, f"{label}:{line_number}: invalid YAML scalar: {exc}")
            return None
        parent[key] = value
        if isinstance(value, dict):
            stack.append((indent, value))
    return root


def validate_skill(plugin_root: Path, validator: Validator) -> None:
    skill_root = plugin_root / "skills" / SKILL_NAME
    skill_md = skill_root / "SKILL.md"
    if not validator.require_file(skill_md, "skill SKILL.md"):
        return
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if not validator.check(match is not None, "SKILL.md must start with closed YAML frontmatter"):
        return
    frontmatter = parse_simple_yaml(match.group(1), validator, "SKILL.md frontmatter")
    if frontmatter is None:
        return
    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    validator.check(not (set(frontmatter) - allowed), "SKILL.md frontmatter has unsupported fields")
    name = frontmatter.get("name")
    validator.check(name == SKILL_NAME, f"skill name must be {SKILL_NAME!r}")
    validator.check(isinstance(name, str) and SKILL_NAME_RE.fullmatch(name) is not None and len(name) <= 64, "skill name must be valid hyphen-case")
    description = frontmatter.get("description")
    validator.check(
        _non_empty_string(description)
        and len(description) <= 1024
        and "<" not in description
        and ">" not in description
        and not description.startswith("[TODO:"),
        "skill description is invalid or unfinished",
    )
    body = text[match.end() :]
    validator.check(
        re.search(r"(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$", body) is None,
        "SKILL.md body contains an unfinished TODO marker",
    )

    openai_yaml_path = skill_root / "agents" / "openai.yaml"
    if not validator.require_file(openai_yaml_path, "skill agents/openai.yaml"):
        return
    openai_yaml = parse_simple_yaml(
        openai_yaml_path.read_text(encoding="utf-8"), validator, "agents/openai.yaml"
    )
    if openai_yaml is None:
        return
    validator.check(not (set(openai_yaml) - {"interface", "policy", "dependencies"}), "agents/openai.yaml has unsupported top-level fields")
    interface = openai_yaml.get("interface")
    validator.check(isinstance(interface, dict), "skill interface must be an object")
    if isinstance(interface, dict):
        allowed_interface = {
            "display_name",
            "short_description",
            "icon_small",
            "icon_large",
            "brand_color",
            "default_prompt",
        }
        validator.check(not (set(interface) - allowed_interface), "skill interface has unsupported fields")
        validator.check(interface.get("display_name") == "Ultra Orchestration", "skill display_name must be Ultra Orchestration")
        short = interface.get("short_description")
        validator.check(_non_empty_string(short) and 25 <= len(short) <= 64, "skill short_description must be 25-64 characters")
        prompt = interface.get("default_prompt")
        validator.check(
            _non_empty_string(prompt) and f"${SKILL_NAME}" in prompt,
            f"skill default_prompt must mention ${SKILL_NAME}",
        )
        color = interface.get("brand_color")
        if color is not None:
            validator.check(isinstance(color, str) and HEX_COLOR_RE.fullmatch(color) is not None, "skill brand_color must use #RRGGBB")
        for key in ("icon_small", "icon_large"):
            asset = resolve_archive_file(skill_root, plugin_root, interface.get(key))
            validator.check(asset is not None and asset.is_file(), f"skill {key} points to a missing or unsafe asset")
    policy = openai_yaml.get("policy")
    if policy is not None:
        validator.check(
            isinstance(policy, dict)
            and not (set(policy) - {"allow_implicit_invocation"})
            and isinstance(policy.get("allow_implicit_invocation"), bool),
            "skill policy must contain only boolean allow_implicit_invocation",
        )

    references = skill_root / "references"
    for name in sorted(REQUIRED_REFERENCES):
        validator.require_file(references / name, f"skill reference {name}")
        validator.check(f"references/{name}" in text, f"SKILL.md must route to references/{name}")


def validate_model_policy(plugin_root: Path, validator: Validator) -> None:
    path = plugin_root / "skills" / SKILL_NAME / "references" / "model-policy.json"
    policy = load_json(path, validator, "model policy")
    if policy is None:
        return
    expected_fields = {
        "schema_version",
        "primary_worker",
        "worker_reasoning_effort",
        "fallback_strategy",
        "allow_host_default_fallback",
    }
    validator.check(set(policy) == expected_fields, "model policy fields do not match schema version 1")
    validator.check(policy.get("schema_version") == 1, "model policy schema_version must be 1")
    worker = policy.get("primary_worker")
    validator.check(
        _non_empty_string(worker) and worker == worker.casefold(),
        "model policy primary_worker must be a non-empty normalized slug",
    )
    validator.check(
        policy.get("worker_reasoning_effort") in {"low", "medium", "high", "xhigh"},
        "model policy worker_reasoning_effort is unsupported",
    )
    validator.check(policy.get("fallback_strategy") == "return-to-parent", "model fallback must return to parent")
    validator.check(isinstance(policy.get("allow_host_default_fallback"), bool), "model host-default fallback flag must be boolean")
    loader = plugin_root / "hooks" / "lib" / "policy_loader.py"
    if validator.require_file(loader, "model policy loader"):
        loader_text = loader.read_text(encoding="utf-8")
        validator.check("model-policy.json" in loader_text, "runtime must load the central model-policy.json")
        if isinstance(worker, str):
            validator.check(worker not in loader_text, "runtime policy loader must not duplicate the worker slug")


def _command_targets(command: str) -> list[str]:
    targets: list[str] = []
    pattern = re.compile(r"\$\{PLUGIN_ROOT\}((?:[/\\][^\"']+)+)")
    for match in pattern.finditer(command):
        targets.append(match.group(1).replace("\\", "/").lstrip("/"))
    return targets


def validate_hooks(plugin_root: Path, manifest: Optional[Mapping[str, Any]], validator: Validator) -> None:
    path = plugin_root / "hooks" / "hooks.json"
    config = load_json(path, validator, "hook configuration")
    if config is None:
        return
    if manifest is not None:
        validator.check("hooks" not in manifest, "hooks configuration must stay out of plugin manifest")
    validator.check(not (set(config) - {"description", "hooks"}), "hook configuration has unsupported root fields")
    validator.check(_non_empty_string(config.get("description")), "hook configuration description is required")
    hooks = config.get("hooks")
    if not validator.check(isinstance(hooks, dict), "hook configuration hooks must be an object"):
        return
    event_names = set(hooks)
    validator.check(event_names == EXPECTED_HOOK_EVENTS, "hook events must match the runtime-supported lifecycle set")
    validator.check(not (event_names - KNOWN_HOOK_EVENTS), "hook configuration contains an unknown event")
    for event_name, groups in hooks.items():
        if not isinstance(groups, list) or not groups:
            validator.check(False, f"hook event {event_name} must contain at least one matcher group")
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, dict):
                validator.check(False, f"hook event {event_name} group {group_index} must be an object")
                continue
            validator.check(not (set(group) - {"matcher", "hooks"}), f"hook event {event_name} group has unsupported fields")
            actions = group.get("hooks")
            if not isinstance(actions, list) or not actions:
                validator.check(False, f"hook event {event_name} group {group_index} needs command actions")
                continue
            if event_name == "SessionStart":
                matcher = group.get("matcher")
                validator.check(
                    isinstance(matcher, str)
                    and {"startup", "resume", "clear", "compact"}.issubset(set(matcher.split("|"))),
                    "SessionStart matcher must cover startup, resume, clear, and compact",
                )
            for action_index, action in enumerate(actions):
                label = f"hook event {event_name} action {action_index}"
                if not isinstance(action, dict):
                    validator.check(False, f"{label} must be an object")
                    continue
                validator.check(
                    not (set(action) - {"type", "command", "commandWindows", "timeout", "additionalContextLimit"}),
                    f"{label} has unsupported fields",
                )
                validator.check(action.get("type") == "command", f"{label} type must be command")
                for command_key in ("command", "commandWindows"):
                    command = action.get(command_key)
                    validator.check(_non_empty_string(command), f"{label} {command_key} is required")
                    if isinstance(command, str):
                        targets = _command_targets(command)
                        validator.check(bool(targets), f"{label} {command_key} must use PLUGIN_ROOT")
                        for target in targets:
                            validator.check((plugin_root / target).is_file(), f"{label} references missing command file {target}")
                timeout = action.get("timeout")
                validator.check(
                    isinstance(timeout, int) and not isinstance(timeout, bool) and 1 <= timeout <= 60,
                    f"{label} timeout must be between 1 and 60 seconds",
                )
                if "additionalContextLimit" in action:
                    limit = action["additionalContextLimit"]
                    validator.check(
                        isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 10000,
                        f"{label} additionalContextLimit must be a positive bounded integer",
                    )
    runtime_source = (plugin_root / "hooks" / "runtime.py").read_text(encoding="utf-8")
    for event_name in EXPECTED_HOOK_EVENTS:
        validator.check(event_name in runtime_source, f"runtime does not recognize configured event {event_name}")


def _call_name(node: ast.Call) -> str:
    parts: list[str] = []
    current: ast.AST = node.func
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _contains_sensitive_expression(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and SENSITIVE_NAME_RE.search(child.id):
            return True
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            if child.value in {"prompt", "transcript", "source_code", "repository_path", "absolute_path"}:
                return True
    return False


def validate_python_and_runtime_security(plugin_root: Path, validator: Validator) -> None:
    parsed: dict[Path, ast.Module] = {}
    for path in sorted(plugin_root.rglob("*.py")):
        try:
            parsed[path] = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            validator.check(True, f"Python syntax is valid: {path}")
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            validator.check(False, f"invalid Python source {path}: {exc}")

    hooks_root = plugin_root / "hooks"
    for path, tree in parsed.items():
        try:
            path.relative_to(hooks_root)
        except ValueError:
            continue
        source = path.read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [(node.module or "").split(".", 1)[0]]
            else:
                modules = []
            for module in modules:
                if not module:
                    continue
                validator.check(module not in FORBIDDEN_NETWORK_MODULES, f"network module {module!r} imported by {path}")
                validator.check(module in ALLOWED_RUNTIME_IMPORTS, f"non-standard runtime dependency {module!r} imported by {path}")
            if isinstance(node, ast.Call):
                name = _call_name(node)
                if name in {"eval", "exec", "compile", "__import__"}:
                    validator.check(False, f"dynamic code execution call {name} is forbidden in {path}")
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                        validator.check(keyword.value.value is False, f"shell=True is forbidden in {path}")
                sinks = {
                    "print",
                    "json.dump",
                    "sys.stdout.write",
                    "sys.stderr.write",
                }
                sink_suffixes = (
                    ".debug",
                    ".info",
                    ".warning",
                    ".error",
                    ".exception",
                    ".critical",
                    ".write",
                    ".write_text",
                    ".write_bytes",
                )
                if name in sinks or name.endswith(sink_suffixes):
                    if any(_contains_sensitive_expression(argument) for argument in node.args):
                        validator.check(False, f"sensitive prompt/source data reaches output or persistence sink {name} in {path}")
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if value is not None and _contains_sensitive_expression(value):
                    if any(isinstance(target, (ast.Subscript, ast.Attribute)) for target in targets):
                        validator.check(False, f"sensitive prompt/source data is assigned into persistent-looking state in {path}")
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                validator.check(
                    NETWORK_URL_RE.search(node.value) is None,
                    f"network URL literal is forbidden in hook runtime {path}",
                )

        if "subprocess" in source:
            validator.check("shell=False" in source, f"subprocess-using runtime file must explicitly use shell=False: {path}")

    forbidden_shell_network = re.compile(
        r"(?im)^\s*(?:curl|wget|nc|ncat|telnet)\b|\b(?:Invoke-WebRequest|Invoke-RestMethod)\b"
    )
    for path in sorted(list(hooks_root.rglob("*.sh")) + list(hooks_root.rglob("*.ps1"))):
        source = path.read_text(encoding="utf-8")
        validator.check(forbidden_shell_network.search(source) is None, f"network command is forbidden in hook launcher {path}")
        validator.check(NETWORK_URL_RE.search(source) is None, f"network URL is forbidden in hook launcher {path}")


def validate_state_persistence(plugin_root: Path, validator: Validator) -> None:
    path = plugin_root / "hooks" / "lib" / "state_store.py"
    if not validator.require_file(path, "state store"):
        return
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    default_keys: Optional[set[str]] = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "default_state":
            for child in ast.walk(node):
                if isinstance(child, ast.Return) and isinstance(child.value, ast.Dict):
                    keys = {
                        key.value
                        for key in child.value.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    }
                    default_keys = keys
                    break
    validator.check(
        default_keys == {"schema_version", "global", "projects", "sessions", "one_shot"},
        "state root schema must contain only versioned orchestration state",
    )
    forbidden_persistence_keys = {
        "prompt",
        "transcript",
        "source",
        "source_code",
        "repository_path",
        "absolute_path",
        "cwd",
        "working_directory",
    }
    string_constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    found = sorted(forbidden_persistence_keys & string_constants)
    validator.check(not found, f"state store contains forbidden persisted field names: {', '.join(found)}")
    validator.check("state-v1.json" in string_constants, "state store must use the versioned plugin-owned state filename")


def validate_json_files(plugin_root: Path, validator: Validator) -> None:
    for path in sorted(plugin_root.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
            validator.check(True, f"JSON is valid: {path}")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
            validator.check(False, f"invalid JSON file {path}: {exc}")


def validate_reviewer_cases(plugin_root: Path, validator: Validator) -> None:
    path = plugin_root / "evals" / "reviewer-cases.json"
    data = load_json(path, validator, "reviewer cases")
    if data is None:
        return
    validator.check(data.get("schema_version") == 1, "reviewer cases schema_version must be 1")
    validator.check(data.get("plugin") == PLUGIN_NAME, "reviewer cases plugin name is invalid")
    validator.check(data.get("version") == "0.1.1", "reviewer cases version must be 0.1.1")
    setup = data.get("shared_setup")
    validator.check(
        isinstance(setup, dict)
        and all(_non_empty_string(value) for value in setup.values()),
        "reviewer shared_setup must be a non-empty string map",
    )
    cases = data.get("cases")
    if not validator.check(isinstance(cases, list), "reviewer cases must be an array"):
        return
    positives = [case for case in cases if isinstance(case, dict) and case.get("type") == "positive"]
    negatives = [case for case in cases if isinstance(case, dict) and case.get("type") == "negative"]
    validator.check(len(cases) == 8, "reviewer dataset must contain exactly eight cases")
    validator.check(len(positives) == 5, "reviewer dataset must contain exactly five positive cases")
    validator.check(len(negatives) == 3, "reviewer dataset must contain exactly three negative cases")
    ids: set[str] = set()
    for index, case in enumerate(cases):
        if not validator.check(isinstance(case, dict), f"reviewer case {index} must be an object"):
            continue
        case_id = case.get("id")
        validator.check(
            isinstance(case_id, str) and SKILL_NAME_RE.fullmatch(case_id) is not None,
            f"reviewer case {index} has an invalid id",
        )
        validator.check(case_id not in ids, f"duplicate reviewer case id: {case_id}")
        if isinstance(case_id, str):
            ids.add(case_id)
        validator.check(case.get("type") in {"positive", "negative"}, f"reviewer case {index} has an invalid type")
        for field in ("user_prompt", "fixture", "expected_behavior", "expected_result_shape"):
            validator.check(_non_empty_string(case.get(field)), f"reviewer case {case_id} is missing {field}")
        if case.get("type") == "negative":
            validator.check(
                _non_empty_string(case.get("why_plugin_should_not_complete")),
                f"negative reviewer case {case_id} needs a safety rationale",
            )


def validate_png_files(plugin_root: Path, validator: Validator) -> None:
    required = {
        plugin_root / "assets" / "composer-icon.png": 48,
        plugin_root / "assets" / "logo.png": 256,
    }
    for path, minimum in sorted(required.items()):
        if not validator.require_file(path, f"required PNG asset {path.name}"):
            continue
        try:
            header = path.read_bytes()[:24]
        except OSError as exc:
            validator.check(False, f"unable to read PNG asset {path}: {exc}")
            continue
        valid_header = (
            len(header) == 24
            and header[:8] == b"\x89PNG\r\n\x1a\n"
            and header[12:16] == b"IHDR"
        )
        if not validator.check(valid_header, f"invalid PNG header: {path}"):
            continue
        width, height = struct.unpack(">II", header[16:24])
        validator.check(width == height, f"PNG asset must be square: {path}")
        validator.check(
            width == minimum,
            f"PNG asset must be exactly {minimum}x{minimum}: {path}",
        )


def validate_svg_files(plugin_root: Path, validator: Validator) -> None:
    required = {
        plugin_root / "assets" / "icon.svg",
        plugin_root / "assets" / "logo.svg",
        plugin_root / "skills" / SKILL_NAME / "assets" / "icon.svg",
        plugin_root / "skills" / SKILL_NAME / "assets" / "logo.svg",
    }
    for path in sorted(required):
        validator.require_file(path, f"required SVG asset {path.name}")
    for path in sorted(plugin_root.rglob("*.svg")):
        try:
            tree = ET.parse(path)
        except (OSError, ET.ParseError) as exc:
            validator.check(False, f"invalid SVG XML {path}: {exc}")
            continue
        root = tree.getroot()
        local_name = root.tag.rsplit("}", 1)[-1]
        validator.check(local_name == "svg", f"SVG root element is invalid: {path}")
        validator.check(_non_empty_string(root.attrib.get("viewBox")), f"SVG must declare viewBox: {path}")
        child_names = [child.tag.rsplit("}", 1)[-1] for child in root.iter()]
        validator.check("title" in child_names, f"SVG must include an accessible title: {path}")
        validator.check(not ({"script", "foreignObject"} & set(child_names)), f"SVG contains executable or foreign content: {path}")
        for element in root.iter():
            for value in element.attrib.values():
                validator.check(
                    not isinstance(value, str) or ("://" not in value and not value.startswith("//")),
                    f"SVG contains an external resource reference: {path}",
                )


def is_generated_benchmark_final_message(path: Path, repo_root: Path) -> bool:
    """Return whether a Markdown file is a model-generated benchmark transcript."""

    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    parts = relative.parts
    return (
        len(parts) >= 5
        and parts[0] == "benchmarks"
        and parts[1] == "runs"
        and "_artifacts" in parts[3:-1]
        and parts[-1] == "final_message.md"
    )


def validate_documents(plugin_root: Path, repo_root: Path, manifest: Optional[Mapping[str, Any]], validator: Validator) -> None:
    for relative in sorted(REQUIRED_DOCUMENTS):
        path = plugin_root / relative
        validator.require_file(path, f"required document {relative}")
        if path.is_file():
            validator.check(bool(path.read_text(encoding="utf-8").strip()), f"document is empty: {relative}")

    for relative in sorted(ROOT_PUBLIC_DOCUMENTS):
        path = repo_root / relative
        validator.require_file(path, f"required root public document {relative}")
        if path.is_file():
            validator.check(
                bool(path.read_text(encoding="utf-8").strip()),
                f"root public document is empty: {relative}",
            )

    i18n_root = plugin_root / "docs" / "i18n"
    actual_i18n = {
        path.relative_to(i18n_root).as_posix()
        for path in i18n_root.glob("*.md")
        if path.is_file()
    }
    validator.check(
        actual_i18n == EXPECTED_I18N_DOCUMENTS,
        "five-language public document set must be exactly English, Korean, Japanese, Simplified Chinese, and Russian",
    )

    license_path = plugin_root / "LICENSE"
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        validator.check("MIT License" in license_text, "LICENSE must contain the MIT License text")
    changelog = plugin_root / "CHANGELOG.md"
    if changelog.is_file() and manifest is not None:
        validator.check(str(manifest.get("version", "")) in changelog.read_text(encoding="utf-8"), "CHANGELOG must mention the manifest version")

    root_license = repo_root / "LICENSE"
    if root_license.is_file() and license_path.is_file():
        validator.check(
            root_license.read_bytes() == license_path.read_bytes(),
            "root and packaged MIT licenses must be byte-identical",
        )

    for path in sorted(repo_root.rglob("*.md")):
        if is_generated_benchmark_final_message(path, repo_root):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            validator.check(False, f"unable to read Markdown file {path}: {exc}")
            continue
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = match.group(1) or match.group(2) or ""
            raw_target = raw_target.strip().strip("<>")
            if not raw_target or raw_target.startswith("#"):
                continue
            parsed = urlparse(raw_target)
            if parsed.scheme or raw_target.startswith("//"):
                continue
            file_part = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
            if not file_part:
                continue
            target = (path.parent / file_part).resolve()
            try:
                target.relative_to(repo_root.resolve())
                inside_repo = True
            except ValueError:
                inside_repo = False
            validator.check(inside_repo and target.exists(), f"broken or escaping Markdown link in {path}: {raw_target}")


def validate_required_layout(plugin_root: Path, repo_root: Path, validator: Validator) -> None:
    for relative in sorted(REQUIRED_PACKAGE_FILES):
        validator.require_file(plugin_root / relative, f"required package file {relative}")
    validator.require_file(
        repo_root / ".github" / "workflows" / "ci.yml", "repository CI workflow"
    )


def validate_no_local_absolute_paths(repo_root: Path, plugin_root: Path, validator: Validator) -> None:
    config_paths = {
        repo_root / ".agents" / "plugins" / "marketplace.json",
        plugin_root / ".codex-plugin" / "plugin.json",
        plugin_root / "hooks" / "hooks.json",
        plugin_root / "skills" / SKILL_NAME / "agents" / "openai.yaml",
        plugin_root / "skills" / SKILL_NAME / "references" / "model-policy.json",
        repo_root / ".github" / "workflows" / "ci.yml",
        plugin_root / "pyproject.toml",
    }
    for path in sorted(config_paths):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        validator.check(WINDOWS_ABSOLUTE_RE.search(text) is None, f"machine-local Windows path found in configuration: {path}")
        validator.check(USER_POSIX_ABSOLUTE_RE.search(text) is None, f"machine-local POSIX home path found in configuration: {path}")


def parse_args() -> argparse.Namespace:
    script_plugin_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", type=Path, default=script_plugin_root)
    parser.add_argument("--repo-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plugin_root = args.plugin_root.expanduser().resolve()
    repo_root = (
        args.repo_root.expanduser().resolve()
        if args.repo_root is not None
        else plugin_root.parents[1]
    )
    validator = Validator()
    validator.check(plugin_root.is_dir(), f"plugin root does not exist: {plugin_root}")
    validator.check(repo_root.is_dir(), f"repository root does not exist: {repo_root}")

    manifest = validate_manifest(plugin_root, validator)
    validate_marketplace(repo_root, plugin_root, manifest, validator)
    validate_hooks(plugin_root, manifest, validator)
    validate_skill(plugin_root, validator)
    validate_model_policy(plugin_root, validator)
    validate_json_files(plugin_root, validator)
    validate_reviewer_cases(plugin_root, validator)
    validate_svg_files(plugin_root, validator)
    validate_png_files(plugin_root, validator)
    validate_python_and_runtime_security(plugin_root, validator)
    validate_state_persistence(plugin_root, validator)
    validate_documents(plugin_root, repo_root, manifest, validator)
    validate_required_layout(plugin_root, repo_root, validator)
    validate_no_local_absolute_paths(repo_root, plugin_root, validator)

    if validator.errors:
        print(f"Package validation failed: {plugin_root}")
        for error in validator.errors:
            print(f"- {error}")
        print(f"Assertions evaluated: {validator.assertions}")
        return 1
    print(f"Package validation passed: {plugin_root}")
    print(f"Assertions evaluated: {validator.assertions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
