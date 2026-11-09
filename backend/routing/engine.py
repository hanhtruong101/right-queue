"""Score in-memory rule snapshots. No queries or writes occur here."""
import re
import unicodedata
from dataclasses import dataclass

from cases.models import ServiceRequest


def normalize_text(value: str) -> str:
    folded = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[^\W_]+", folded))


@dataclass(frozen=True)
class Candidate:
    rule_id: int
    name: str
    service_id: int
    team_id: int
    minimum_score: int
    keywords: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class RoutingDecision:
    service_id: int | None
    team_id: int | None
    status: str
    rule_id: int | None
    score: int
    reason: str


def matches_phrase(text: str, phrase: str) -> bool:
    """Both arguments are normalized; spaces enforce whole-word boundaries."""
    return bool(phrase) and f" {phrase} " in f" {text} "


def score_rule(rule, fields):
    return sum(
        weight for phrase, weight in rule.keywords
        if any(matches_phrase(text, phrase) for text in fields)
    )


def select_decision(title, description, candidates):
    # Separate fields so the end of a title cannot invent a phrase with the description.
    fields = (normalize_text(title), normalize_text(description))
    winners = []
    highest = 0
    for rule in candidates:
        score = score_rule(rule, fields)
        if score < rule.minimum_score:
            continue
        if score > highest:
            highest, winners = score, [rule]
        elif score == highest:
            winners.append(rule)

    if len(winners) == 1:
        rule = winners[0]
        return RoutingDecision(
            rule.service_id, rule.team_id, ServiceRequest.Status.QUEUED,
            rule.rule_id, highest, f"Matched rule '{rule.name}' with score {highest}.",
        )
    reason = (
        f"Ambiguous match: multiple rules tied at score {highest}."
        if winners else "No qualifying routing rule."
    )
    return RoutingDecision(None, None, ServiceRequest.Status.PENDING_TRIAGE, None, highest, reason)
