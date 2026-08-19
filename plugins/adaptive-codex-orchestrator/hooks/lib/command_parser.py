"""Conservative Korean/English parser for Ultra Orchestration controls.

The parser intentionally recognizes a narrow command language.  Prompt text is
processed in memory and is never logged or returned in a result.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import unicodedata
from typing import Iterable, Optional, Sequence, Tuple


ALIASES: Tuple[str, ...] = (
    "솔 울트라",
    "울트라 오케스트레이션",
    "스파크 오케스트레이션",
    "적응형 오케스트레이션",
    "sol ultra",
    "ultra orchestration",
    "adaptive orchestration",
    "spark orchestration",
)

_ALIAS_RE = re.compile("|".join(re.escape(value) for value in ALIASES), re.I)
_ORCHESTRATION_ANCHOR_RE = re.compile(
    r"(?:오케스트레이션|orchestration|adaptive-orchestration)", re.I
)

_STATUS_RES: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"(?:상태|status)(?:를|가|는|은)?\s*(?:알려|보여|확인|show|tell)?",
        r"(?:켜져|활성화되어)\s*(?:있어|있나요|있습니까)?",
        r"(?:어떤|무슨|현재)\s*(?:오케스트레이션\s*)?(?:프로필|profile)",
        r"현재\s*(?:어떤|무슨)\s*(?:오케스트레이션\s*)?(?:프로필|profile)",
        r"(?:is|are)\s+(?:ultra\s+)?orchestration\s+(?:on|enabled|active)",
        r"(?:which|what)\s+(?:orchestration\s+)?profile",
        r"show\s+(?:the\s+)?(?:current\s+)?orchestration\s+status",
    )
)

_NEGATIVE_RES: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"켜(?:지|지는)?\s*마(?:라|세요)?",
        r"사용(?:하)?지\s*마(?:라|세요)?",
        r"활성화(?:하)?지\s*마(?:라|세요)?",
        r"do\s+not\s+(?:enable|activate|use|turn\s+on)",
        r"don['’]?t\s+(?:enable|activate|use|turn\s+on)",
    )
)

_DISABLE_RES: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"(?:꺼|끄)(?:줘|\s*줘|주세요|라|고)?",
        r"비활성화(?:해|\s*해|해주세요|하라|하고)?",
        r"사용\s*중지(?:해|\s*해|해주세요)?",
        r"turn\s+sol\s+ultra(?:\s+mode)?\s+off",
        r"turn\s+(?:(?:this\s+mode|it)\s+|(?:ultra\s+)?orchestration\s+)?off",
        r"disable(?:\s+(?:this\s+mode|(?:ultra\s+|adaptive\s+)?orchestration))?",
        r"deactivate(?:\s+(?:this\s+mode|orchestration))?",
    )
)

_ENABLE_RES: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"켜(?:줘|\s*줘|주세요|라|고)?",
        r"(?<!비)활성화(?:해|\s*해|해주세요|하라|하고)?",
        r"적용(?:해|\s*해|해주세요|하라|하고)?",
        r"시작(?:해|\s*해|해주세요|하라|하고)?",
        r"사용(?:해|\s*해|해주세요|하라|하고)?",
        r"(?:빠른|보수적|균형(?:형)?)\s*(?:프로필|모드)?로\s*처리(?:해|\s*해|해주세요)?",
        r"turn\s+sol\s+ultra(?:\s+mode)?\s+on",
        r"turn\s+(?:(?:this\s+mode|it)\s+|(?:sol\s+ultra\s+|ultra\s+)?orchestration\s+)?on",
        r"enable(?:\s+(?:it|this\s+mode|(?:sol\s+ultra\s+|ultra\s+|adaptive\s+)?orchestration))?",
        r"activate(?:\s+(?:it|this\s+mode|orchestration))?",
        r"use(?:\s+(?:it|this\s+mode|(?:sol\s+ultra\s+|ultra\s+|adaptive\s+)?orchestration))?",
    )
)

_PROFILE_ACTION_RE = re.compile(
    r"(?:프로필|profile|모드).{0,80}(?:바꿔|변경|전환|switch|change|set)|"
    r"(?:바꿔|변경|전환|switch|change|set).{0,80}(?:프로필|profile|모드)",
    re.I,
)
_PROFILE_USE_RE = re.compile(
    r"(?:보수적(?:인|으로)?|균형(?:형|적으로)?|빠른|빠르게).{0,24}사용(?:해|\s*해|해주세요)?|"
    r"use\s+(?:the\s+)?(?:conservative|balanced|fast)\s+profile",
    re.I,
)
_EXPLICIT_ENABLE_RE = re.compile(
    r"켜(?:줘|\s*줘|주세요|라|고)?|(?<!비)활성화|적용(?:해|\s*해)?|시작(?:해|\s*해)?|"
    r"(?:빠른|보수적|균형(?:형)?)\s*(?:프로필|모드)?로\s*처리|"
    r"turn\s+(?:(?:this\s+mode|it)\s+|(?:sol\s+ultra\s+|ultra\s+)?orchestration\s+)?on|"
    r"\b(?:enable|activate)\b",
    re.I,
)
_META_CONTROL_RE = re.compile(
    r"\b(?:how\s+(?:do|can|should|would)\s+(?:i|we)|(?:can|should|would)\s+(?:i|we)|"
    r"explain\s+how\s+to|tell\s+me\s+how\s+to)\b.{0,120}"
    r"\b(?:enable|disable|activate|deactivate|use|turn\s+(?:on|off))\b|"
    r"(?:어떻게|방법을?|해야\s*(?:할까|하나요|합니까)).{0,50}"
    r"(?:켜|끄|꺼|활성화|비활성화|사용)|"
    r"(?:켜|끄|꺼|활성화|비활성화|사용).{0,24}(?:방법|해야\s*(?:할까|하나요|합니까))",
    re.I,
)

_SCOPES: Tuple[Tuple[str, Tuple[re.Pattern[str], ...]], ...] = (
    (
        "one-shot",
        tuple(
            re.compile(pattern, re.I)
            for pattern in (
                r"이번\s*(?:작업|요청|일)(?:에서)?만",
                r"이\s*(?:작업|요청)(?:에서)?만",
                r"(?:for\s+)?this\s+(?:task|request)\s+only",
                r"only\s+for\s+this\s+(?:task|request)",
            )
        ),
    ),
    (
        "project",
        tuple(
            re.compile(pattern, re.I)
            for pattern in (
                r"(?:이|현재)\s*(?:프로젝트|저장소|리포지토리)(?:에서|에서는|에|의)?(?:\s*항상|\s*기본값으로)?",
                r"(?:for|in)\s+(?:this|the\s+current)\s+(?:repository|repo|project)",
                r"(?:for|in)\s+the\s+current\s+(?:repository|repo|project)",
            )
        ),
    ),
    (
        "global",
        tuple(
            re.compile(pattern, re.I)
            for pattern in (
                r"모든\s*프로젝트(?:에서)?(?:\s*기본으로)?",
                r"(?:내\s*)?(?:codex\s*)?전체\s*기본(?:값|\s*설정)?(?:에서|으로)?",
                r"(?:globally|global\s+default)",
                r"(?:by\s+default\s+)?for\s+all\s+projects",
                r"by\s+default",
            )
        ),
    ),
    (
        "session",
        tuple(
            re.compile(pattern, re.I)
            for pattern in (
                r"(?:이|현재)\s*세션(?:에서|에는|동안)?",
                r"(?:for\s+)?this\s+session",
                r"(?:for\s+)?the\s+current\s+session",
            )
        ),
    ),
)

_PROFILES: Tuple[Tuple[str, Tuple[re.Pattern[str], ...]], ...] = (
    (
        "conservative",
        tuple(re.compile(pattern, re.I) for pattern in (r"보수적(?:인|으로)?", r"conservative")),
    ),
    (
        "balanced",
        tuple(re.compile(pattern, re.I) for pattern in (r"균형(?:형|적으로)?", r"balanced")),
    ),
    (
        "fast",
        tuple(re.compile(pattern, re.I) for pattern in (r"빠른|빠르게", r"fast")),
    ),
)

_UNKNOWN_PROFILE_RE = re.compile(
    r"(?:초고속|터보|공격적|최대|turbo|aggressive|maximum)\s*(?:프로필|profile|모드)?",
    re.I,
)
_REFERENTIAL_RE = re.compile(r"(?:이\s*모드|this\s+mode|\bit\b)", re.I)
_TASK_SIGNAL_RE = re.compile(
    r"(?:분석|수정|구현|검증|테스트|리뷰|조사|원인|찾|고쳐|작성|추가|삭제|리팩터|병렬|통합|"
    r"analy[sz]|fix|implement|inspect|investigate|review|validate|test|find|debug|build|write|add|remove|refactor|integrate)",
    re.I,
)


@dataclass(frozen=True)
class ParseResult:
    """A serializable parser decision without original user text."""

    intent: Optional[str] = None
    scope: Optional[str] = None
    profile: Optional[str] = None
    confidence: str = "none"
    ambiguous: bool = False
    reason: Optional[str] = None
    contains_remaining_task: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize_preserving_whitespace(value: object) -> str:
    if not isinstance(value, str):
        return ""
    # Python strings may contain isolated surrogate code points.  NFKC can
    # retain them safely; replacing them keeps all later regex work portable.
    value = value.encode("utf-8", "replace").decode("utf-8")
    return unicodedata.normalize("NFKC", value).casefold()


def _normalize(value: object) -> str:
    return re.sub(r"\s+", " ", _normalize_preserving_whitespace(value)).strip()


def _mask_examples(value: str, *, collapse: bool = True) -> str:
    value = re.sub(r"```.*?```|~~~.*?~~~", " ", value, flags=re.S)
    value = re.sub(r"`[^`\r\n]*`", " ", value)
    value = re.sub(r'"[^"\r\n]*"|“[^”\r\n]*”|‘[^’\r\n]*’|\'[^\'\r\n]*\'', " ", value)
    value = re.sub(r"(?m)^\s*>.*$", " ", value)
    return re.sub(r"\s+", " ", value).strip() if collapse else value


def _edge_candidate(original: str, masked_multiline: str) -> Tuple[str, bool]:
    long_input = len(original) > 1000 or original.count("\n") > 12
    if not long_input:
        return _normalize(masked_multiline), False
    lines = [line.strip() for line in masked_multiline.splitlines() if line.strip()]
    edge = " ".join(lines[:3] + lines[-3:])
    return _normalize(edge), True


def _matches(patterns: Iterable[re.Pattern[str]], value: str) -> bool:
    return any(pattern.search(value) for pattern in patterns)


def _matched_names(
    groups: Sequence[Tuple[str, Sequence[re.Pattern[str]]]], value: str
) -> Tuple[str, ...]:
    return tuple(name for name, patterns in groups if _matches(patterns, value))


def _has_remaining_task(value: str, control_patterns: Iterable[re.Pattern[str]]) -> bool:
    if _TASK_SIGNAL_RE.search(value):
        # Control verbs such as "변경" are removed below before the final call;
        # task-specific signals survive and make mixed commands explicit.
        pass
    residual = value
    for pattern in control_patterns:
        residual = pattern.sub(" ", residual)
    residual = _ALIAS_RE.sub(" ", residual)
    residual = _ORCHESTRATION_ANCHOR_RE.sub(" ", residual)
    residual = re.sub(
        r"\b(?:please|the|a|an|for|in|on|to|of|this|current|all|globally|global|"
        r"session|project|repository|repo|task|request|only|default|profile|mode|"
        r"show|tell|me|is|are|which|what|switch|change|set|turn|enable|disable|use|it)\b",
        " ",
        residual,
        flags=re.I,
    )
    residual = re.sub(
        r"(?:이번|이|현재|모든|내|전체|기본|기본값|프로젝트|저장소|리포지토리|세션|"
        r"작업|요청|일|프로필|모드|상태|알려|보여|확인|켜져|있어|항상|사용|처리|"
        r"바꿔|변경|전환|활성화|비활성화|적용|시작|기본으로|에서는|에서|으로|로|을|를|은|는|만|해|줘)",
        " ",
        residual,
    )
    residual = re.sub(r"[^0-9a-z가-힣]+", " ", residual, flags=re.I).strip()
    return bool(residual and (_TASK_SIGNAL_RE.search(residual) or len(residual) >= 3))


def parse_command(
    text: object,
    *,
    mode_active: bool = False,
    skill_invoked: bool = False,
) -> ParseResult:
    """Parse a deterministic control command.

    Referential controls ("turn this mode off") are accepted only when an
    explicit skill invocation supplies the missing subject. ``mode_active`` is
    retained for API compatibility, but active state alone cannot prove which
    mode a pronoun or demonstrative refers to.
    """

    normalized_multiline = _normalize_preserving_whitespace(text)
    if not normalized_multiline.strip():
        return ParseResult()
    masked_multiline = _mask_examples(normalized_multiline, collapse=False)
    if not masked_multiline.strip():
        return ParseResult()
    candidate, long_input = _edge_candidate(normalized_multiline, masked_multiline)
    alias = bool(_ALIAS_RE.search(candidate))
    orchestration_anchor = bool(_ORCHESTRATION_ANCHOR_RE.search(candidate))
    unique_anchor = alias or orchestration_anchor

    status = _matches(_STATUS_RES, candidate)
    if status and unique_anchor:
        return ParseResult(intent="status", confidence="high")

    # Explanatory and deliberative questions mention control verbs but are not
    # control commands. Polite imperatives such as "Can you enable ...?" remain
    # command-like; first-person "Can I ...?" does not mutate state.
    if _META_CONTROL_RE.search(candidate):
        return ParseResult()

    negative = _matches(_NEGATIVE_RES, candidate)
    disable = negative or _matches(_DISABLE_RES, candidate)
    enable = _matches(_ENABLE_RES, candidate)

    # Explicit negation wins over an enable token inside the same phrase.
    if negative:
        enable = False

    scopes = _matched_names(_SCOPES, candidate)
    profiles = _matched_names(_PROFILES, candidate)

    if len(scopes) > 1:
        return ParseResult(
            confidence="low", ambiguous=True, reason="conflicting scopes"
        )
    if len(profiles) > 1:
        return ParseResult(
            confidence="low", ambiguous=True, reason="conflicting profiles"
        )
    if _UNKNOWN_PROFILE_RE.search(candidate) and ("프로필" in candidate or "profile" in candidate):
        return ParseResult(
            confidence="low", ambiguous=True, reason="unknown profile"
        )

    profile = profiles[0] if profiles else None
    scope = scopes[0] if scopes else None
    profile_use = bool(profile and _PROFILE_USE_RE.search(candidate))
    profile_change = bool(
        profile and (_PROFILE_ACTION_RE.search(candidate) or profile_use)
    )
    if profile_use and not _EXPLICIT_ENABLE_RE.search(candidate):
        enable = False

    if enable and disable:
        return ParseResult(
            confidence="low", ambiguous=True, reason="conflicting enable and disable actions"
        )

    # Long pasted material must place an explicit alias and action at an edge.
    if long_input and not (alias and (enable or disable or profile_change)):
        return ParseResult()

    intent: Optional[str]
    if disable:
        intent = "disable"
    elif enable:
        intent = "enable"
    elif profile_change:
        intent = "set_profile"
    else:
        return ParseResult()

    explicit_subject = unique_anchor
    referential_only = bool(
        _REFERENTIAL_RE.search(candidate)
        and not unique_anchor
    )
    if intent in {"enable", "disable"} and referential_only and not skill_invoked:
        return ParseResult(
            confidence="low",
            ambiguous=True,
            reason="referential control without an explicit orchestration anchor",
        )
    if intent == "disable" and not explicit_subject:
        if not scope and not (
            _REFERENTIAL_RE.search(candidate) and skill_invoked
        ):
            return ParseResult(
                confidence="low",
                ambiguous=True,
                reason="disable without an explicit orchestration anchor",
            )

    # Canonical one-shot/profile shorthand deliberately permits no alias.
    one_shot_profile_shorthand = scope == "one-shot" and profile is not None and enable
    if not explicit_subject and not profile_change and not one_shot_profile_shorthand:
        korean_scoped_shorthand = bool(
            scope in {"project", "global"}
            and (enable or disable)
            and "모드" not in candidate
        )
        referential_control_allowed = bool(
            _REFERENTIAL_RE.search(candidate) and skill_invoked
        )
        if not (
            korean_scoped_shorthand or referential_control_allowed
        ):
            return ParseResult()

    if intent in {"enable", "disable"}:
        scope = scope or "session"
    elif intent == "set_profile":
        scope = scope or "session"

    all_control_patterns = [
        *_STATUS_RES,
        *_NEGATIVE_RES,
        *_DISABLE_RES,
        *_ENABLE_RES,
        _PROFILE_ACTION_RE,
        _PROFILE_USE_RE,
        _UNKNOWN_PROFILE_RE,
    ]
    for _, patterns in _SCOPES:
        all_control_patterns.extend(patterns)
    for _, patterns in _PROFILES:
        all_control_patterns.extend(patterns)

    remaining = _has_remaining_task(candidate, all_control_patterns)
    return ParseResult(
        intent=intent,
        scope=scope,
        profile=profile,
        confidence="high" if explicit_subject or profile_change else "medium",
        contains_remaining_task=remaining,
    )


__all__ = ["ALIASES", "ParseResult", "parse_command"]
