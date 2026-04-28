"""CLI entrypoint for the Tech Decision Copilot demo."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .memory import SessionMemory
from .reporting import render_markdown_report
from .workflow import run_decision_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Tech Decision Copilot demo.")
    parser.add_argument("--question", required=True, help="Natural language tech decision question.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    memory = SessionMemory()
    report = run_decision_workflow(args.question, memory=memory)
    print(render_markdown_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
