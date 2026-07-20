#!/usr/bin/env python3
"""Create a printable, no-solutions worksheet from the Motion practice cards."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
TWO_COLUMN_GAP = 0.3 * inch
TWO_COLUMN_WIDTH = (QUESTION_WIDTH - TWO_COLUMN_GAP) / 2
UNITS_WORKSPACE_LINES = 4
UNITS_QUESTIONS_PER_COLUMN = 5
UNITS_SOURCE_PAGE = ROOT / "notes/review/units/index.html"
WORKSHEET_TITLE_OVERRIDES = {
    ROOT / "notes/momentum/conservation/index.html": "Momentum Conservation",
}


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
            if heading.startswith("Practice"):
                self.practice_article_depth = self.article_depth
        elif tag == "details" and self.card_parts is not None:
            self.details_depth -= 1
        elif tag == "div" and self.card_parts is not None:
            self.card_depth -= 1
            if self.card_depth == 0:
                text = re.sub(r"\s+", " ", " ".join(self.card_parts)).strip()
                if text.startswith("Example:"):
                    self.questions.append(text.removeprefix("Example:").strip())
                elif text.startswith("Question:"):
                    self.questions.append(text.removeprefix("Question:").strip())
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


@dataclass(frozen=True)
class PracticePage:
    """A notes page that has student-facing questions in a Practice section."""

    source: Path
    title: str
    slug: str
    questions: tuple[str, ...]


def practice_questions(source_page: Path = SOURCE_PAGE) -> list[str]:
    """Return direct practice-card prompts, excluding solutions and Reading cards."""

    parser = PracticeCardParser()
    parser.feed(source_page.read_text(encoding="utf-8"))
    if not parser.questions:
        raise ValueError(f"No practice questions were found in {source_page}.")
    return parser.questions


def page_title(source_page: Path) -> str:
    """Read the browser title so the worksheet has the same lesson name as its notes page."""

    match = re.search(r"<title>\s*(.*?)\s*</title>", source_page.read_text(encoding="utf-8"), re.DOTALL)
    if match is None:
        raise ValueError(f"No HTML title was found in {source_page}.")
    return re.sub(r"\s+", " ", match.group(1)).strip()


def practice_pages() -> list[PracticePage]:
    """Find every notes page that contains direct student prompts in a Practice section."""

    candidates: list[tuple[Path, tuple[str, ...]]] = []
    for source_page in sorted((ROOT / "notes").glob("**/index.html")):
        try:
            questions = practice_questions(source_page)
        except ValueError:
            continue
        candidates.append((source_page, tuple(questions)))

    leaf_counts: dict[str, int] = {}
    for source_page, _questions in candidates:
        leaf_counts[source_page.parent.name] = leaf_counts.get(source_page.parent.name, 0) + 1

    pages: list[PracticePage] = []
    for source_page, questions in candidates:
        leaf_name = source_page.parent.name
        slug = leaf_name
        if leaf_counts[leaf_name] > 1:
            slug = f"{source_page.parent.parent.name}-{leaf_name}"
        pages.append(
            PracticePage(
                source=source_page,
                title=page_title(source_page),
                slug=slug,
                questions=questions,
            )
        )
    return pages


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


def two_column_question_height(question: str, number: int) -> float:
    """Return the space for a compact Unit-conversion question and its workspace."""

    wrapped_question = simpleSplit(f"{number}. {question}", "Helvetica", QUESTION_FONT_SIZE, TWO_COLUMN_WIDTH)
    workspace_height = UNITS_WORKSPACE_LINES * SPACE_LINE_HEIGHT
    return (len(wrapped_question) * QUESTION_LEADING) + 14 + workspace_height + 18


def page_count(questions: list[str], extra_lines: int | list[int]) -> int:
    """Calculate the page count for a title page and later pages with shared margins."""

    if isinstance(extra_lines, int):
        workspace_extras = [extra_lines] * len(questions)
    else:
        if len(extra_lines) != len(questions):
            raise ValueError("Each question needs one workspace-line count.")
        workspace_extras = extra_lines

    pages = 1
    y = FIRST_PAGE_QUESTION_Y
    for number, (question, workspace_extra) in enumerate(zip(questions, workspace_extras), start=1):
        block_height = question_block_height(question, number, workspace_extra)
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


def workspace_extra_lines(questions: list[str]) -> list[int]:
    """Balance workspace across an even number of printable pages when possible."""

    target_pages = page_count(questions, extra_lines=0)
    if target_pages % 2:
        target_pages += 1

    extras = [choose_workspace_extra_lines(questions)] * len(questions)
    next_question = 0
    while True:
        fitting_question: int | None = None
        for offset in range(len(questions)):
            question_index = (next_question + offset) % len(questions)
            candidate = extras.copy()
            candidate[question_index] += 1
            if page_count(questions, candidate) <= target_pages:
                fitting_question = question_index
                break
        if fitting_question is None:
            return extras
        extras[fitting_question] += 1
        next_question = (fitting_question + 1) % len(questions)


def draw_column_divider(canvas: Canvas, top: float) -> None:
    """Draw a quiet center rule beneath a two-column worksheet's title area."""

    canvas.setLineWidth(0.5)
    canvas.setStrokeColorRGB(0.65, 0.65, 0.65)
    canvas.line(PAGE_WIDTH / 2, BOTTOM_MARGIN, PAGE_WIDTH / 2, top)
    canvas.setStrokeColorRGB(0, 0, 0)


def draw_units_column(
    canvas: Canvas,
    entries: list[tuple[int, str]],
    x_position: float,
    top: float,
) -> None:
    """Draw one evenly spaced Units column from its top to the bottom margin."""

    heights = [two_column_question_height(question, number) for number, question in entries]
    available_height = top - BOTTOM_MARGIN
    if sum(heights) > available_height:
        raise ValueError("Units column does not fit on the page.")
    extra_space = (available_height - sum(heights)) / len(entries)
    y = top

    for (number, question), required_height in zip(entries, heights):
        wrapped_question = simpleSplit(
            f"{number}. {question}", "Helvetica", QUESTION_FONT_SIZE, TWO_COLUMN_WIDTH
        )
        canvas.setFont("Helvetica", QUESTION_FONT_SIZE)
        for line in wrapped_question:
            canvas.drawString(x_position, y, line)
            y -= QUESTION_LEADING
        y -= required_height - (len(wrapped_question) * QUESTION_LEADING) + extra_space


def build_units_two_column_pdf(canvas: Canvas, questions: list[str]) -> None:
    """Lay out Units prompts in balanced two-column pages with evenly shared workspace."""

    entries = list(enumerate(questions, start=1))
    columns = [
        entries[index:index + UNITS_QUESTIONS_PER_COLUMN]
        for index in range(0, len(entries), UNITS_QUESTIONS_PER_COLUMN)
    ]
    page_number = 0
    while columns:
        left_column = columns.pop(0)
        right_column = columns.pop(0) if columns else []
        if not right_column and len(left_column) > 1:
            split_index = (len(left_column) + 1) // 2
            right_column = left_column[split_index:]
            left_column = left_column[:split_index]

        top = FIRST_PAGE_QUESTION_Y if page_number == 0 else LATER_PAGE_QUESTION_Y
        draw_column_divider(canvas, top)
        draw_units_column(canvas, left_column, LEFT_MARGIN, top)
        if right_column:
            right_x_position = LEFT_MARGIN + TWO_COLUMN_WIDTH + TWO_COLUMN_GAP
            draw_units_column(canvas, right_column, right_x_position, top)

        page_number += 1
        if columns:
            canvas.showPage()


def build_pdf(
    output_path: Path,
    source_page: Path = SOURCE_PAGE,
    title: str | None = None,
) -> int:
    """Create one printable, questions-only worksheet for a notes Practice section."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output_path), pagesize=letter)
    lesson_title = WORKSHEET_TITLE_OVERRIDES.get(source_page, title or page_title(source_page))
    canvas.setTitle(f"{lesson_title} Practice Questions")
    canvas.setAuthor("Physics Notes")
    questions = practice_questions(source_page)
    canvas.setFont("Helvetica", 15)
    canvas.drawString(LEFT_MARGIN, PAGE_HEIGHT - 0.9 * inch, f"{lesson_title.lower()} - practice problems")

    if source_page == UNITS_SOURCE_PAGE:
        build_units_two_column_pdf(canvas, questions)
        canvas.save()
        return len(questions)

    extra_lines = workspace_extra_lines(questions)
    y = FIRST_PAGE_QUESTION_Y
    for number, (question, workspace_extra) in enumerate(zip(questions, extra_lines), start=1):
        wrapped_question = simpleSplit(f"{number}. {question}", "Helvetica", QUESTION_FONT_SIZE, QUESTION_WIDTH)
        required_height = question_block_height(question, number, workspace_extra)
        if y - required_height < BOTTOM_MARGIN:
            canvas.showPage()
            y = LATER_PAGE_QUESTION_Y

        canvas.setFont("Helvetica", QUESTION_FONT_SIZE)
        for line in wrapped_question:
            canvas.drawString(LEFT_MARGIN, y, line)
            y -= QUESTION_LEADING
        y -= 14 + ((workspace_line_count(question) + workspace_extra) * SPACE_LINE_HEIGHT) + 18

    canvas.save()
    return len(questions)


def build_all_pdfs(output_directory: Path = ROOT / "output/pdf") -> dict[str, int]:
    """Create a worksheet PDF for every Practice section in the notes."""

    generated: dict[str, int] = {}
    for page in practice_pages():
        output_path = output_directory / f"{page.slug}-practice-questions.pdf"
        generated[page.slug] = build_pdf(output_path, source_page=page.source, title=page.title)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for the generated PDF.")
    parser.add_argument("--all", action="store_true", help="Generate worksheets for every Practice section.")
    args = parser.parse_args()
    if args.all:
        generated = build_all_pdfs()
        print(f"Generated {len(generated)} practice worksheets.")
        return
    question_count = build_pdf(args.output)
    print(f"Generated {args.output} with {question_count} questions.")


if __name__ == "__main__":
    main()
