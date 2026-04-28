"""Session-scoped memory for the Tech Decision Copilot demo."""

from __future__ import annotations


class SessionMemory:
    """Stores only the parts of a conversation that affect later decisions."""

    def __init__(self) -> None:
        self._questions: list[str] = []
        self._constraints: list[str] = []
        self._recommendations: list[str] = []

    def record(self, question: str, constraints: list[str], recommendation: str) -> None:
        self._questions.append(question)
        self._constraints.extend(item for item in constraints if item not in self._constraints)
        if recommendation:
            self._recommendations.append(recommendation)

    def snapshot(self) -> dict[str, list[str]]:
        return {
            "questions": list(self._questions),
            "constraints": list(self._constraints),
            "recommendations": list(self._recommendations),
        }
