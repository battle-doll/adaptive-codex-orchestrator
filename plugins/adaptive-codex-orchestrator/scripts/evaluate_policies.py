#!/usr/bin/env python3
"""Validate the offline orchestration policy-eval dataset deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


REQUIRED_FIELDS = {
    "id",
    "prompt_or_scenario",
    "expected_delegation_decision",
    "expected_worker_count_range",
    "expected_worker_role",
    "expected_writer_count",
    "expected_parent_responsibility",
    "expected_fallback",
    "expected_safety_behavior",
}
REQUIRED_SCENARIOS = {
    "trivial-one-line-edit",
    "one-focused-file-change",
    "parallel-read-only-exploration",
    "five-independent-module-inspections",
    "overlapping-write-tasks",
    "architecture-decision",
    "authentication-change",
    "database-migration",
    "test-failure-analysis",
    "narrow-reproducible-bug",
    "large-ambiguous-production-incident",
    "spark-unavailable",
    "spark-rate-limited",
    "explicit-model-selection-unsupported",
    "mode-enabled-and-task-combined",
    "mode-disabled",
    "non-sol-parent",
    "multimodal-task",
    "context-too-large-for-spark",
    "worker-result-lacking-evidence",
    "conflicting-worker-conclusions",
    "worker-scope-expansion",
    "worker-nested-delegation-attempt",
    "fast-profile-disjoint-writes",
    "fast-profile-overlapping-writes",
    "user-task-cap-one",
    "user-task-cap-zero",
    "delegated-exploration-no-parent-duplication",
    "worker-result-six-fields",
    "requested-vs-confirmed-worker-model",
    "small-four-module-map-parent-only",
}
ALLOWED_DECISIONS = {"parent-only", "delegate", "conditional", "disabled"}
ALLOWED_ROLES = {
    "Spark Explorer",
    "Spark Worker",
    "Spark Tester",
    "Generic bounded worker",
}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORKER_RESULT_FIELDS = (
    "conclusion",
    "evidence",
    "files_and_lines",
    "tests_or_checks",
    "risks",
    "recommended_parent_action",
)
WORKER_RESULT_SCHEMA_TEXT = ", ".join(WORKER_RESULT_FIELDS)


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _contains_text(values: object, phrase: str) -> bool:
    return isinstance(values, list) and any(
        isinstance(item, str) and phrase.casefold() in item.casefold() for item in values
    )


def validate_record(record: object, line_number: int) -> list[str]:
    prefix = f"line {line_number}"
    if not isinstance(record, dict):
        return [f"{prefix}: record must be a JSON object"]

    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(record))
    extra = sorted(set(record) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"{prefix}: missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix}: unexpected fields: {', '.join(extra)}")
    if missing:
        return errors

    scenario_id = record["id"]
    if not isinstance(scenario_id, str) or ID_RE.fullmatch(scenario_id) is None:
        errors.append(f"{prefix}: id must be lower-case hyphen-case")
        scenario_id = f"line-{line_number}"
    label = f"{prefix} ({scenario_id})"

    prompt = record["prompt_or_scenario"]
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append(f"{label}: prompt_or_scenario must be a non-empty string")

    decision = record["expected_delegation_decision"]
    if decision not in ALLOWED_DECISIONS:
        errors.append(f"{label}: invalid expected_delegation_decision")

    count_range = record["expected_worker_count_range"]
    minimum = maximum = None
    if not isinstance(count_range, dict) or set(count_range) != {"min", "max"}:
        errors.append(f"{label}: expected_worker_count_range must contain only min and max")
    else:
        minimum = count_range["min"]
        maximum = count_range["max"]
        if not _is_int(minimum) or not _is_int(maximum):
            errors.append(f"{label}: worker-count bounds must be integers")
        elif not 0 <= minimum <= maximum <= 6:
            errors.append(f"{label}: worker-count bounds must satisfy 0 <= min <= max <= 6")

    roles = record["expected_worker_role"]
    if not isinstance(roles, list) or not all(role in ALLOWED_ROLES for role in roles):
        errors.append(f"{label}: expected_worker_role contains an unsupported role")
        roles = []
    elif len(roles) != len(set(roles)):
        errors.append(f"{label}: expected_worker_role must not contain duplicates")

    writers = record["expected_writer_count"]
    if not _is_int(writers) or not 0 <= writers <= 1:
        errors.append(f"{label}: expected_writer_count must be zero or one")
    elif _is_int(maximum) and writers > maximum:
        errors.append(f"{label}: writer count cannot exceed maximum worker count")

    if not _non_empty_strings(record["expected_parent_responsibility"]):
        errors.append(f"{label}: expected_parent_responsibility must be a non-empty string array")
    fallback = record["expected_fallback"]
    if not isinstance(fallback, str) or not fallback.strip():
        errors.append(f"{label}: expected_fallback must be a non-empty string")
    if not _non_empty_strings(record["expected_safety_behavior"]):
        errors.append(f"{label}: expected_safety_behavior must be a non-empty string array")

    if decision in {"parent-only", "disabled"} and maximum != 0:
        errors.append(f"{label}: {decision} scenarios must have zero workers")
    if decision == "delegate" and (_is_int(minimum) and minimum < 1):
        errors.append(f"{label}: delegated scenarios require at least one worker")
    if maximum == 0 and roles:
        errors.append(f"{label}: zero-worker scenarios must not name worker roles")
    if _is_int(maximum) and maximum > 0 and not roles:
        errors.append(f"{label}: worker scenarios must name at least one role")
    if _is_int(writers) and writers > 0 and "Spark Worker" not in roles:
        errors.append(f"{label}: writer scenarios must include the Spark Worker role")

    if scenario_id in {
        "parallel-read-only-exploration",
        "five-independent-module-inspections",
        "delegated-exploration-no-parent-duplication",
    }:
        if maximum != 2 or writers != 0 or roles != ["Spark Explorer"]:
            errors.append(
                f"{label}: substantial structural mapping requires at most two read-only Explorers"
            )
        if not _contains_text(
            record["expected_safety_behavior"], "substantial independent evidence"
        ):
            errors.append(
                f"{label}: delegated mapping must justify startup and integration cost"
            )
    if scenario_id == "small-four-module-map-parent-only" and (
        decision != "parent-only" or maximum != 0 or fallback != "none"
    ):
        errors.append(
            f"{label}: small, obvious module mapping must default to the parent"
        )
    if scenario_id == "one-focused-file-change" and (
        decision != "parent-only" or maximum != 0
    ):
        errors.append(f"{label}: a clear single-file change must stay in the parent")
    if scenario_id in {"narrow-reproducible-bug", "mode-enabled-and-task-combined"}:
        if maximum != 1 or writers != 0 or "Spark Explorer" not in roles:
            errors.append(f"{label}: a local reproducible bug permits at most one read-only Explorer")
    if scenario_id == "overlapping-write-tasks":
        if maximum != 1 or writers != 0 or "Spark Explorer" not in roles:
            errors.append(f"{label}: shared-state work permits one read-only Explorer and parent writes")
    if scenario_id == "fast-profile-overlapping-writes" and writers != 1:
        errors.append(f"{label}: overlapping writes must remain limited to one writer")
    if scenario_id == "fast-profile-disjoint-writes" and writers != 1:
        errors.append(f"{label}: fast-profile disjoint writes must still use one concurrent writer")
    if scenario_id == "worker-nested-delegation-attempt" and not _contains_text(
        record["expected_safety_behavior"], "nested delegation without exception"
    ):
        errors.append(f"{label}: nested delegation must be forbidden without exception")
    if scenario_id in {
        "spark-unavailable",
        "spark-rate-limited",
        "explicit-model-selection-unsupported",
    }:
        if fallback != "return-to-parent":
            errors.append(f"{label}: worker failure/capability fallback must return to parent")
        if not _contains_text(record["expected_safety_behavior"], "single spawn attempt"):
            errors.append(f"{label}: worker failure/capability handling requires a single spawn attempt")
        if not _contains_text(record["expected_safety_behavior"], "host-default"):
            errors.append(f"{label}: worker failure/capability handling must reject host-default fallback")
    if scenario_id == "user-task-cap-one" and (minimum, maximum) != (0, 1):
        errors.append(
            f"{label}: an explicit user cap of one is a ceiling, not a worker target"
        )
    if scenario_id == "user-task-cap-zero":
        if maximum != 0 or decision != "parent-only":
            errors.append(f"{label}: a zero user cap must force parent-only execution")
        if not _contains_text(record["expected_safety_behavior"], "internal no-worker reason"):
            errors.append(f"{label}: the no-worker path must record an internal reason")
    if scenario_id == "trivial-one-line-edit" and not _contains_text(
        record["expected_safety_behavior"], "internal no-worker reason"
    ):
        errors.append(f"{label}: direct execution must record an internal no-worker reason")
    if scenario_id == "delegated-exploration-no-parent-duplication" and not _contains_text(
        record["expected_safety_behavior"], "do not repeat broad exploration"
    ):
        errors.append(f"{label}: the parent must not repeat delegated broad exploration")
    if scenario_id == "worker-result-six-fields":
        if not _contains_text(
            record["expected_safety_behavior"], "exactly these six top-level fields"
        ):
            errors.append(f"{label}: result contract must require exactly six top-level fields")
        if not _contains_text(record["expected_safety_behavior"], WORKER_RESULT_SCHEMA_TEXT):
            errors.append(
                f"{label}: result schema must list exactly: {WORKER_RESULT_SCHEMA_TEXT}"
            )
    if scenario_id == "requested-vs-confirmed-worker-model":
        if not _contains_text(record["expected_safety_behavior"], "requested model"):
            errors.append(f"{label}: requested model setting must be recorded separately")
        if not _contains_text(record["expected_safety_behavior"], "confirmed model"):
            errors.append(f"{label}: confirmed model fact must be recorded separately")
    return errors


def validate_dataset(path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return 0, [f"unable to read {path}: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"line {line_number}: blank lines are not allowed in JSONL")
            continue
        try:
            record = json.loads(line, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, DuplicateKeyError) as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        errors.extend(validate_record(record, line_number))
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            scenario_id = record["id"]
            if scenario_id in seen:
                errors.append(
                    f"line {line_number}: duplicate id {scenario_id!r}; first seen on line {seen[scenario_id]}"
                )
            else:
                seen[scenario_id] = line_number
            records.append(record)

    missing_scenarios = sorted(REQUIRED_SCENARIOS - set(seen))
    if missing_scenarios:
        errors.append(f"missing required scenarios: {', '.join(missing_scenarios)}")
    if len(records) < 25:
        errors.append(f"dataset must contain at least 25 records; found {len(records)}")
    return len(records), errors


def parse_args() -> argparse.Namespace:
    default_path = Path(__file__).resolve().parent.parent / "evals" / "prompts.jsonl"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=Path, default=default_path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.dataset.expanduser().resolve()
    count, errors = validate_dataset(path)
    if errors:
        print(f"Policy eval validation failed: {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Policy eval validation passed: {count} scenarios ({path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
