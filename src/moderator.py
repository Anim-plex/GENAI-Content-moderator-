from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence
import re
from collections import Counter


AI_DISCLOSURE_PATTERNS = (
    r"\bas an ai\b",
    r"\bas a language model\b",
    r"\bi am an ai\b",
    r"\bai[- ]generated\b",
    r"\bai[- ]written\b",
)

SPAM_PATTERNS = (
    r"\bfree\b",
    r"\bclick here\b",
    r"\bsubscribe\b",
    r"\bvisit\b",
    r"\bearn\b",
    r"\bbuy now\b",
)

TOXIC_PATTERNS = (
    r"\bidiot\b",
    r"\bstupid\b",
    r"\bhate\b",
    r"\bkill\b",
)

SENSITIVE_PATTERNS = (
    r"\bssn\b",
    r"\bcredit card\b",
    r"\bpassword\b",
    r"\bsocial security\b",
)


@dataclass
class ModerationConfig:
    ai_disclosure_patterns: Sequence[str] = AI_DISCLOSURE_PATTERNS
    spam_patterns: Sequence[str] = SPAM_PATTERNS
    toxic_patterns: Sequence[str] = TOXIC_PATTERNS
    sensitive_patterns: Sequence[str] = SENSITIVE_PATTERNS
    max_repetition_ratio: float = 0.25
    max_duplicate_sentence_ratio: float = 0.35
    min_unique_word_ratio: float = 0.35


@dataclass
class ModerationResult:
    text: str
    score: float
    flags: Dict[str, bool]
    reasons: Dict[str, List[str]]
    signals: Dict[str, float] = field(default_factory=dict)

    def is_flagged(self) -> bool:
        return any(self.flags.values())


WORD_RE = re.compile(r"[a-zA-Z0-9']+")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _pattern_hits(text: str, patterns: Iterable[str]) -> List[str]:
    hits = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(pattern)
    return hits


def _unique_word_ratio(words: List[str]) -> float:
    if not words:
        return 1.0
    unique = len(set(words))
    return unique / len(words)


def _repetition_ratio(words: List[str]) -> float:
    if not words:
        return 0.0
    counts = Counter(words)
    repeated = sum(count for count in counts.values() if count > 1)
    return repeated / len(words)


def _duplicate_sentence_ratio(sentences: List[str]) -> float:
    cleaned = [s.strip().lower() for s in sentences if s.strip()]
    if not cleaned:
        return 0.0
    counts = Counter(cleaned)
    duplicates = sum(1 for count in counts.values() if count > 1)
    return duplicates / len(cleaned)


def moderate_text(text: str, config: ModerationConfig | None = None) -> ModerationResult:
    config = config or ModerationConfig()
    normalized = _normalize(text)
    words = WORD_RE.findall(normalized)
    sentences = [sentence.strip() for sentence in SENTENCE_RE.findall(text)]

    ai_hits = _pattern_hits(normalized, config.ai_disclosure_patterns)
    spam_hits = _pattern_hits(normalized, config.spam_patterns)
    toxic_hits = _pattern_hits(normalized, config.toxic_patterns)
    sensitive_hits = _pattern_hits(normalized, config.sensitive_patterns)

    unique_ratio = _unique_word_ratio(words)
    repetition_ratio = _repetition_ratio(words)
    duplicate_sentence_ratio = _duplicate_sentence_ratio(sentences)

    flags = {
        "ai_disclosure": bool(ai_hits),
        "spam": bool(spam_hits),
        "toxic": bool(toxic_hits),
        "sensitive": bool(sensitive_hits),
        "high_repetition": repetition_ratio > config.max_repetition_ratio,
        "low_unique_words": unique_ratio < config.min_unique_word_ratio,
        "duplicate_sentences": duplicate_sentence_ratio > config.max_duplicate_sentence_ratio,
    }

    reasons = {
        "ai_disclosure": ai_hits,
        "spam": spam_hits,
        "toxic": toxic_hits,
        "sensitive": sensitive_hits,
        "repetition": [f"repetition_ratio={repetition_ratio:.2f}"]
        if flags["high_repetition"]
        else [],
        "unique_words": [f"unique_word_ratio={unique_ratio:.2f}"]
        if flags["low_unique_words"]
        else [],
        "duplicate_sentences": [f"duplicate_sentence_ratio={duplicate_sentence_ratio:.2f}"]
        if flags["duplicate_sentences"]
        else [],
    }

    score = 0.0
    score += 0.3 if flags["ai_disclosure"] else 0.0
    score += 0.2 if flags["spam"] else 0.0
    score += 0.2 if flags["toxic"] else 0.0
    score += 0.2 if flags["sensitive"] else 0.0
    score += 0.1 if flags["high_repetition"] else 0.0
    score += 0.1 if flags["low_unique_words"] else 0.0
    score += 0.1 if flags["duplicate_sentences"] else 0.0
    score = min(score, 1.0)

    signals = {
        "unique_word_ratio": unique_ratio,
        "repetition_ratio": repetition_ratio,
        "duplicate_sentence_ratio": duplicate_sentence_ratio,
    }

    return ModerationResult(
        text=text,
        score=score,
        flags=flags,
        reasons=reasons,
        signals=signals,
    )
