"""Data models for the Tech Decision Copilot demo."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceItem:
    source: str
    summary: str
    supports: str


@dataclass(slots=True)
class CandidateAnalysis:
    option: str
    pros: list[str]
    cons: list[str]
    best_for: str


@dataclass(slots=True)
class Recommendation:
    option: str
    rationale: str
    confidence: str


@dataclass(slots=True)
class DecisionReport:
    problem_statement: str
    evaluation_dimensions: list[str]
    candidates: list[CandidateAnalysis]
    evidence: list[EvidenceItem]
    recommendation: Recommendation
    risks: list[str]
    follow_ups: list[str]
    needs_clarification: bool = False
    missing_information: list[str] = field(default_factory=list)
