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
PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 0.65 * inch
RIGHT_MARGIN = PAGE_WIDTH - 0.65 * inch
BOTTOM_MARGIN = 0.65 * inch
QUESTION_WIDTH = RIGHT_MARGIN - LEFT_MARGIN
QUESTION_FONT_SIZE = 10.5
QUESTION_LEADING = 14.5
SPACE_LINE_HEIGHT = 14
FIRST_PAGE_QUESTION_Y = PAGE_HEIGHT - 1.25 * inch
LATER_PAGE_QUESTION_Y = PAGE_HEIGHT - 0.8 * inch


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


def question_block_height(question: str, number: int, extra_lines: int) -> float:
    """Return the vertical space used by one question and its blank workspace."""

    wrapped_question = simpleSplit(f"{number}. {question}", "Helvetica", QUESTION_FONT_SIZE, QUESTION_WIDTH)
    workspace_height = (workspace_line_count(question) + extra_lines) * SPACE_LINE_HEIGHT
    return (len(wrapped_question) * QUESTION_LEADING) + 14 + workspace_height + 18


def page_count(questions: list[str], extra_lines: int) -> int:
    """Calculate the page count for a title page and later pages with shared margins."""

    pages = 1
    y = FIRST_PAGE_QUESTION_Y
    for number, question in enumerate(questions, start=1):
        block_height = question_block_height(question, number, extra_lines)
        if y - block_height < BOTTOM_MARGIN:
            pages += 1
            y = LATER_PAGE_QUESTION_Y
        y -= block_height
    return pages


def choose_workspace_extra_lines(questions: list[str]) -> int:
    """Maximize evenly distributed workspace without adding another sheet side."""

    target_pages = page_count(questions, extra_lines=0)
    if target_pages % 2:
        target_pages += 1
    fitting_extras = [
        extra_lines
        for extra_lines in range(9)
        if page_count(questions, extra_lines) == target_pages
    ]
    return max(fitting_extras, default=0)


def build_pdf(output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output_path), pagesize=letter)
    canvas.setTitle("Motion Practice Questions")
    canvas.setAuthor("Physics Notes")
    questions = practice_questions()
    extra_lines = choose_workspace_extra_lines(questions)
    canvas.setFont("Helvetica", 15)
    canvas.drawString(LEFT_MARGIN, PAGE_HEIGHT - 0.9 * inch, "motion - practice problems")
    y = FIRST_PAGE_QUESTION_Y
    for number, question in enumerate(questions, start=1):
        wrapped_question = simpleSplit(f"{number}. {question}", "Helvetica", QUESTION_FONT_SIZE, QUESTION_WIDTH)
        required_height = question_block_height(question, number, extra_lines)
        if y - required_height < BOTTOM_MARGIN:
            canvas.showPage()
            y = LATER_PAGE_QUESTION_Y

        canvas.setFont("Helvetica", QUESTION_FONT_SIZE)
        for line in wrapped_question:
            canvas.drawString(LEFT_MARGIN, y, line)
            y -= QUESTION_LEADING
        y -= 14 + ((workspace_line_count(question) + extra_lines) * SPACE_LINE_HEIGHT) + 18

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
