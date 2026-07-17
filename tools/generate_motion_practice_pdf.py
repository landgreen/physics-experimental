#!/usr/bin/env python3
"""Create a printable, no-solutions worksheet from the Motion practice cards."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from html.parser import HTMLParser

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "notes/motion/motion/index.html"
DEFAULT_OUTPUT = ROOT / "output/pdf/motion-practice-questions.pdf"


class PracticeCardParser(HTMLParser):
    """Extract direct Example cards from the Practice article using only the standard library."""

    def __init__(self) -> None:
        super().__init__()
        self.article_depth = 0
        self.practice_article_depth: int | None = None
        self.collecting_heading = False
        self.heading_parts: list[str] = []
        self.card_parts: list[str] | None = None
        self.card_depth = 0
        self.details_depth = 0
        self.questions: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            self.article_depth += 1
        elif tag == "h1" and self.article_depth:
            self.collecting_heading = True
            self.heading_parts = []
        elif tag == "div" and self.practice_article_depth == self.article_depth:
            classes = dict(attrs).get("class", "").split()
            if self.card_parts is None and "example" in classes:
                self.card_parts = []
                self.card_depth = 1
            elif self.card_parts is not None:
                self.card_depth += 1
        elif tag == "details" and self.card_parts is not None:
            self.details_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self.collecting_heading:
            self.collecting_heading = False
            heading = " ".join(self.heading_parts).strip()
            if heading == "Practice":
                self.practice_article_depth = self.article_depth
        elif tag == "details" and self.card_parts is not None:
            self.details_depth -= 1
        elif tag == "div" and self.card_parts is not None:
            self.card_depth -= 1
            if self.card_depth == 0:
                text = re.sub(r"\s+", " ", " ".join(self.card_parts)).strip()
                if text.startswith("Example:"):
                    self.questions.append(text.removeprefix("Example:").strip())
                self.card_parts = None
        elif tag == "article":
            if self.practice_article_depth == self.article_depth:
                self.practice_article_depth = None
            self.article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.collecting_heading:
            self.heading_parts.append(data)
        if self.card_parts is not None and self.details_depth == 0:
            self.card_parts.append(data)


def practice_questions() -> list[str]:
    """Return direct practice-card prompts, excluding solutions and the Reading card."""

    parser = PracticeCardParser()
    parser.feed(SOURCE_PAGE.read_text(encoding="utf-8"))
    if not parser.questions:
        raise ValueError("No Motion practice questions were found.")
    return parser.questions


def workspace_line_count(question: str) -> int:
    """Give longer prompts slightly more workspace while keeping the worksheet compact."""

    if len(question) > 300:
        return 8
    if len(question) > 190:
        return 6
    return 5


def build_pdf(output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output_path), pagesize=letter)
    canvas.setTitle("Motion Practice Questions")
    canvas.setAuthor("Physics Notes")
    page_width, page_height = letter
    left_margin = 0.65 * inch
    right_margin = page_width - 0.65 * inch
    bottom_margin = 0.65 * inch
    question_width = right_margin - left_margin
    question_font_size = 10.5
    question_leading = 14.5
    line_height = 14
    y = page_height - 0.8 * inch
    questions = practice_questions()
    for number, question in enumerate(questions, start=1):
        wrapped_question = simpleSplit(f"{number}. {question}", "Helvetica", question_font_size, question_width)
        required_height = (len(wrapped_question) * question_leading) + 15 + (workspace_line_count(question) * line_height) + 18
        if y - required_height < bottom_margin:
            canvas.showPage()
            y = page_height - 0.8 * inch

        canvas.setFont("Helvetica", question_font_size)
        for line in wrapped_question:
            canvas.drawString(left_margin, y, line)
            y -= question_leading
        y -= 14 + (workspace_line_count(question) * line_height) + 18

    canvas.save()
    return len(questions)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for the generated PDF.")
    args = parser.parse_args()
    question_count = build_pdf(args.output)
    print(f"Generated {args.output} with {question_count} questions.")


if __name__ == "__main__":
    main()
