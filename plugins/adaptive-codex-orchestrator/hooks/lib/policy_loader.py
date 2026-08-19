"""Load packaged policies from fixed plugin-owned paths only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


PROFILE_LIMITS = {
    "conservative": {"max_workers": 2, "max_writers": 1, "max_retries": 0},
    "balanced": {"max_workers": 4, "max_writers": 1, "max_retries": 0},
    "fast": {"max_workers": 6, "max_writers": 1, "max_retries": 0},
}
ACTIVE_POLICY_REVISION = 3


class PolicyError(ValueError):
    pass


def reference_dir(plugin_root: Path) -> Path:
    return Path(plugin_root) / "skills" / "adaptive-orchestration" / "references"


def load_model_policy(plugin_root: Path) -> dict:
    path = reference_dir(plugin_root) / "model-policy.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PolicyError("model policy is unavailable") from exc
    if not isinstance(value, Mapping) or value.get("schema_version") != 1:
        raise PolicyError("unsupported model policy schema")
    worker = value.get("primary_worker")
    effort = value.get("worker_reasoning_effort")
    if not isinstance(worker, str) or not worker or effort not in {
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
    }:
        raise PolicyError("invalid model policy")
    if value.get("fallback_strategy") != "return-to-parent" or not isinstance(
        value.get("allow_host_default_fallback"), bool
    ):
        raise PolicyError("invalid model fallback policy")
    return dict(value)


def load_runtime_policy(plugin_root: Path, profile: str) -> str:
    if profile not in PROFILE_LIMITS:
        raise PolicyError("unknown profile")
    model = load_model_policy(plugin_root)
    try:
        template = (reference_dir(plugin_root) / "runtime-policy.md").read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeDecodeError) as exc:
        raise PolicyError("runtime policy is unavailable") from exc
    limits = PROFILE_LIMITS[profile]
    replacements = {
        "{{PRIMARY_WORKER}}": model["primary_worker"],
        "{{REASONING_EFFORT}}": model["worker_reasoning_effort"],
        "{{PROFILE}}": profile,
        "{{MAX_WORKERS}}": str(limits["max_workers"]),
        "{{MAX_WRITERS}}": str(limits["max_writers"]),
        "{{MAX_RETRIES}}": str(limits["max_retries"]),
    }
    for marker, replacement in replacements.items():
        template = template.replace(marker, replacement)
    if "{{" in template or "}}" in template:
        raise PolicyError("runtime policy contains an unresolved marker")
    return template.strip()


def compact_reminder(plugin_root: Path, profile: str) -> str:
    model = load_model_policy(plugin_root)
    limits = PROFILE_LIMITS[profile]
    fallback = (
        "If the requested worker cannot start, return the slice to the parent without "
        "retry or host-default substitution."
        if not model["allow_host_default_fallback"]
        else "Use a host-default worker only when the host explicitly supports that fallback."
    )
    return (
        f"Ultra Orchestration is active ({profile}; profile cap {limits['max_workers']}; "
        "concurrent writer cap 1). Direct: one-word, typo, clear single-file, and unsupported-"
        "completion verification tasks use zero workers; a local reproducible bug defaults to "
        "zero and may use at most one read-only evidence Explorer. Four-module mapping defaults "
        "to zero workers when the modules and paired tests are small or obvious; use at most two "
        "disjoint read-only Explorers only when substantial independent evidence makes the expected "
        "saving clearly exceed spawn and integration cost. Shared-state/common-fixture or authentication/"
        "permission/tenant work may use at most one read-only Explorer; the parent writes and "
        "performs final security validation. Otherwise cap workers at the minimum of profile, "
        "host, user, and independently useful slices. The parent integrates, finally validates, "
        "and only spot-checks delegated evidence; never repeat broad exploration. Nested "
        "delegation is forbidden. Load routing, worker, and model references once only before "
        f"an actual spawn; keep a zero-worker reason internal. {fallback}"
    )


def worker_contract(plugin_root: Path, *, confirmed_spark: bool) -> str:
    model = load_model_policy(plugin_root)
    if confirmed_spark:
        identity = (
            f"This SubagentStart hook reports `{model['primary_worker']}` as the active model. "
            "Treat that as a start-time host report, not proof of completed model usage."
        )
    else:
        identity = (
            f"The host did not expose a reliable worker model here. The requested model is "
            f"`{model['primary_worker']}`, but the confirmed model is unavailable; make no "
            "model-specific usage claim."
        )
    return (
        f"{identity}\n\nYou are a bounded delegated worker. Follow the assigned role, objective, "
        "scope, allowed files, forbidden actions, evidence, validation, and return format. "
        "Do not expand scope or spawn another subagent. Explorers and testers are read-only "
        "unless edits were explicitly assigned. A worker changes only assigned files, avoids "
        "unrelated cleanup and new dependencies, and reports every change. Return a compact "
        "structured result with exactly these six top-level fields and no others: conclusion, "
        "evidence, files_and_lines, tests_or_checks, risks, recommended_parent_action. Cite "
        "concrete file/line evidence and exact check outcomes. Do not draft a user-facing final "
        "answer or claim success without verification. The parent owns decisions, integration, "
        "final validation, and the final answer."
    )


__all__ = [
    "PROFILE_LIMITS",
    "ACTIVE_POLICY_REVISION",
    "PolicyError",
    "compact_reminder",
    "load_model_policy",
    "load_runtime_policy",
    "worker_contract",
]
