#!/usr/bin/env python3
"""Create printable, no-solutions worksheets from the Practice cards on each notes page.

Each worksheet is sized for double-sided printing: one sheet (2 pages) when the
questions fit, otherwise two sheets (4 pages). Leftover space on every page is
shared out as extra workspace so the pages come out full.

To leave a card off the printout, add the class "printout-ignore" to its div:
<div class='example printout-ignore'>. Elements inside a card can also use
class="printout-ignore" (for example a reference table).
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "notes/motion/motion/index.html"
DEFAULT_OUTPUT = ROOT / "output/pdf/motion-practice-questions.pdf"
UNITS_SOURCE_PAGE = ROOT / "notes/review/units/index.html"
WORKSHEET_TITLE_OVERRIDES = {
    ROOT / "notes/momentum/conservation/index.html": "Momentum Conservation",
}

PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 0.65 * inch
RIGHT_MARGIN = PAGE_WIDTH - 0.65 * inch
BOTTOM_MARGIN = 0.6 * inch
CONTENT_WIDTH = RIGHT_MARGIN - LEFT_MARGIN
FIRST_PAGE_TOP = PAGE_HEIGHT - 1.15 * inch
LATER_PAGE_TOP = PAGE_HEIGHT - 0.6 * inch
TWO_COLUMN_GAP = 0.3 * inch
TWO_COLUMN_WIDTH = (CONTENT_WIDTH - TWO_COLUMN_GAP) / 2

# Minimum blank workspace under each prompt, in points.
EXAMPLE_WORKSPACE = 84
QUESTION_WORKSPACE = 50
UNITS_WORKSPACE = 44
GAP_AFTER_PROMPT = 6
DIAGRAM_WIDTH = 3.4 * inch
DIAGRAM_MAX_HEIGHT = 1.8 * inch
TARGET_PAGE_OPTIONS = (2, 4)

FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"
for regular, bold in (
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
):
    if Path(regular).is_file() and Path(bold).is_file():
        pdfmetrics.registerFont(TTFont("WorksheetFont", regular))
        pdfmetrics.registerFont(TTFont("WorksheetFont-Bold", bold))
        FONT, BOLD_FONT = "WorksheetFont", "WorksheetFont-Bold"
        break

PROMPT_STYLE = ParagraphStyle("prompt", fontName=FONT, fontSize=10.5, leading=14.5)


# --------------------------------------------------------------------------- parsing


@dataclass
class PracticeItem:
    """One printable card: its prompt, plus any table or diagram the student needs."""

    kind: str  # "Example" or "Question"
    text: str  # plain text of the prompt
    markup: str  # the prompt with <super>/<sub> tags for reportlab
    tables: list[list[list[str]]] = field(default_factory=list)
    svg: str | None = None


def _strip_tags(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _prompt_markup(fragment: str) -> str:
    """Convert a card's HTML prompt into reportlab paragraph markup."""

    fragment = re.sub(r"<sup>(.*?)</sup>", lambda m: "\x01" + _strip_tags(m.group(1)) + "\x02", fragment, flags=re.S)
    fragment = re.sub(r"<sub>(.*?)</sub>", lambda m: "\x03" + _strip_tags(m.group(1)) + "\x04", fragment, flags=re.S)
    text = _clean(_strip_tags(fragment))
    text = html.escape(text, quote=False)
    text = text.replace("\x01", "<super>").replace("\x02", "</super>")
    text = text.replace("\x03", "<sub>").replace("\x04", "</sub>")
    return text


def _practice_section(page_html: str) -> str | None:
    """Return the HTML that holds a page's practice cards.

    Final-layout pages keep everything inside <details class="practice-menu">.
    Older pages start the section with an <h1>Practice</h1> heading.
    """

    menu = re.search(r"<details[^>]*class=['\"][^'\"]*\bpractice-menu\b[^'\"]*['\"][^>]*>", page_html)
    if menu is not None:
        article_end = page_html.find("</article>", menu.end())
        article_end = article_end if article_end != -1 else len(page_html)
        menu_end = page_html.rfind("</details>", menu.end(), article_end)
        return page_html[menu.end(): menu_end if menu_end != -1 else article_end]
    match = re.search(r"<h1[^>]*>\s*Practice\b", page_html)
    if match is None:
        return None
    end = page_html.find("</article>", match.end())
    return page_html[match.end(): end if end != -1 else len(page_html)]


def practice_items(source_page: Path = SOURCE_PAGE) -> list[PracticeItem]:
    """Return the printable practice cards on a notes page, in order."""

    section = _practice_section(source_page.read_text(encoding="utf-8"))
    if section is None:
        raise ValueError(f"No Practice section was found in {source_page}.")
    starts = [m.start() for m in re.finditer(r"<div class=['\"][^'\"]*\bexample\b[^'\"]*['\"]", section)]
    items: list[PracticeItem] = []
    for index, start in enumerate(starts):
        card = section[start: starts[index + 1] if index + 1 < len(starts) else len(section)]
        opening = card[: card.index(">") + 1]
        if "printout-ignore" in opening:
            continue
        card = card[len(opening):]
        card = re.sub(r"<details.*?</details>", " ", card, flags=re.S)
        card = re.sub(r"<(\w+)[^>]*class=['\"][^'\"]*printout-ignore[^'\"]*['\"][^>]*>.*?</\1>", " ", card, flags=re.S)
        card = re.sub(r"<script.*?</script>", " ", card, flags=re.S)
        svg_match = re.search(r"<svg.*?</svg>", card, flags=re.S)
        svg = svg_match.group(0) if svg_match else None
        card = re.sub(r"<svg.*?</svg>", " ", card, flags=re.S)
        tables = []
        for table_html in re.findall(r"<table.*?</table>", card, flags=re.S):
            rows = []
            for row_html in re.findall(r"<tr.*?</tr>", table_html, flags=re.S):
                cells = [_prompt_markup(cell) for cell in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row_html, flags=re.S)]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)
        card = re.sub(r"<table.*?</table>", " ", card, flags=re.S)
        label = re.search(r"<strong>\s*(Example|Question)\s*:?\s*</strong>\s*:?", card)
        if label is None:
            continue  # Reading cards and other non-question cards
        prompt_html = card[label.end():]
        prompt_html = re.sub(r"</div>\s*$", "", prompt_html.strip())
        markup = _prompt_markup(prompt_html)
        if svg:
            markup = markup.replace("the circuit above", "the circuit below").replace("the diagram above", "the diagram below")
        text = _clean(re.sub(r"<[^>]+>", "", markup.replace("<super>", "^")))
        if not text:
            continue
        items.append(PracticeItem(label.group(1), html.unescape(text), markup, tables, svg))
    if not items:
        raise ValueError(f"No practice questions were found in {source_page}.")
    return items


def practice_questions(source_page: Path = SOURCE_PAGE) -> list[str]:
    """Return the plain-text prompts of the printable practice cards."""

    return [item.text for item in practice_items(source_page)]


@dataclass(frozen=True)
class PracticePage:
    """A notes page that has student-facing questions in a Practice section."""

    source: Path
    title: str
    slug: str
    questions: tuple[str, ...]


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
        pages.append(PracticePage(source_page, page_title(source_page), slug, questions))
    return pages


# --------------------------------------------------------------------------- building blocks


def _svg_drawing(svg: str, width: float):
    """Turn an inline SVG diagram into a scaled reportlab drawing."""

    from svglib.svglib import svg2rlg

    svg = re.sub(r"\son\w+=(\"[^\"]*\"|'[^']*')", "", svg)  # drop mouseover scripts
    svg = re.sub(r"<g[^>]*fade-volts.*?</g>", "", svg, flags=re.S)  # drop hidden hover overlays
    svg = svg.replace("'", '"')
    svg = re.sub(r"\s+<tspan", "<tspan", svg)  # svglib turns the line break before a subscript into a gap
    if "xmlns=" not in svg:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    drawing = svg2rlg(StringIO(svg))
    if drawing is None:
        return None
    scale = min(width / drawing.width, DIAGRAM_MAX_HEIGHT / drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)
    return drawing


@dataclass
class Block:
    """A laid-out question: a list of (flowable, height, x offset) plus its workspace."""

    parts: list
    content_height: float
    workspace: float

    @property
    def height(self) -> float:
        return self.content_height + GAP_AFTER_PROMPT + self.workspace


def build_block(item: PracticeItem, number: int, width: float, workspace: float) -> Block:
    """Stack the prompt, any tables, and any diagram. Each part is (flowable, height, x offset, gap after)."""

    parts = []
    paragraph = Paragraph(f"<b>{number}.</b> {item.markup}", PROMPT_STYLE)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    parts.append((paragraph, height, 0, 0))
    for rows in item.tables:
        cells = [[Paragraph(cell, PROMPT_STYLE) for cell in row] for row in rows]
        column_count = max(len(row) for row in rows)
        cells = [row + [""] * (column_count - len(row)) for row in cells]
        column_width = min(1.3 * inch, (width - 0.3 * inch) / column_count)
        table = Table(cells, colWidths=[column_width] * column_count)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        _, table_height = table.wrap(width, PAGE_HEIGHT)
        parts[-1] = parts[-1][:3] + (6,)
        parts.append((table, table_height, 0.2 * inch, 0))
    if item.svg:
        drawing = _svg_drawing(item.svg, min(DIAGRAM_WIDTH, width))
        if drawing is not None:
            parts[-1] = parts[-1][:3] + (6,)
            parts.append((drawing, drawing.height, (width - drawing.width) / 2, 0))
    content = sum(height + gap for _, height, _, gap in parts)
    return Block(parts, content, workspace)


def draw_block(canvas: Canvas, block: Block, x: float, top: float) -> None:
    y = top
    for flowable, height, x_offset, gap in block.parts:
        if isinstance(flowable, (Paragraph, Table)):
            flowable.drawOn(canvas, x + x_offset, y - height)
        else:
            renderPDF.draw(flowable, canvas, x + x_offset, y - height)
        y -= height + gap


def minimum_workspace(item: PracticeItem) -> float:
    return QUESTION_WORKSPACE if item.kind == "Question" else EXAMPLE_WORKSPACE


def paginate(blocks: list[Block]) -> list[list[int]]:
    """Greedily assign blocks to pages, keeping each block on one page."""

    pages: list[list[int]] = [[]]
    remaining = FIRST_PAGE_TOP - BOTTOM_MARGIN
    for index, block in enumerate(blocks):
        if block.height > remaining and pages[-1]:
            pages.append([])
            remaining = LATER_PAGE_TOP - BOTTOM_MARGIN
        pages[-1].append(index)
        remaining -= block.height
    return pages


def layout(items: list[PracticeItem], width: float = CONTENT_WIDTH) -> list[list[Block]]:
    """Choose a 2 or 4 page target and share the free space as workspace."""

    blocks = [build_block(item, n, width, minimum_workspace(item)) for n, item in enumerate(items, start=1)]
    base_pages = len(paginate(blocks))
    target = next((t for t in TARGET_PAGE_OPTIONS if base_pages <= t), base_pages + base_pages % 2)

    # Add the same extra workspace to every block, as much as still fits in the target.
    low, high = 0.0, 400.0
    for _ in range(40):
        middle = (low + high) / 2
        trial = [Block(b.parts, b.content_height, b.workspace + middle) for b in blocks]
        if len(paginate(trial)) <= target:
            low = middle
        else:
            high = middle
    blocks = [Block(b.parts, b.content_height, b.workspace + low) for b in blocks]

    # Share each page's leftover space among the blocks on that page.
    pages = paginate(blocks)
    laid_out = []
    for page_number, indices in enumerate(pages):
        top = FIRST_PAGE_TOP if page_number == 0 else LATER_PAGE_TOP
        leftover = (top - BOTTOM_MARGIN) - sum(blocks[i].height for i in indices)
        share = max(leftover, 0) / len(indices)
        laid_out.append([Block(blocks[i].parts, blocks[i].content_height, blocks[i].workspace + share) for i in indices])
    return laid_out


def page_count(questions_or_items, extra_lines=None) -> int:
    """Number of printed pages a worksheet uses."""

    items = questions_or_items
    if items and isinstance(items[0], str):
        items = [PracticeItem("Example", q, html.escape(q, quote=False)) for q in items]
    return len(layout(list(items)))


# --------------------------------------------------------------------------- drawing


def draw_footer(canvas: Canvas, page_number: int, total: int) -> None:
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(RIGHT_MARGIN, 0.35 * inch, f"page {page_number} of {total}")
    canvas.setFillColor(colors.black)


def build_units_two_column_pdf(canvas: Canvas, items: list[PracticeItem], title: str) -> int:
    """Short Units prompts fit best in two columns."""

    blocks = [build_block(item, n, TWO_COLUMN_WIDTH, UNITS_WORKSPACE) for n, item in enumerate(items, start=1)]
    # fill columns top to bottom, then share the leftover space in each column
    columns: list[list[Block]] = [[]]
    remaining = FIRST_PAGE_TOP - BOTTOM_MARGIN
    for block in blocks:
        if block.height > remaining and columns[-1]:
            columns.append([])
            page_index = len(columns) // 2 + len(columns) % 2 - 1
            remaining = (FIRST_PAGE_TOP if page_index == 0 else LATER_PAGE_TOP) - BOTTOM_MARGIN
        columns[-1].append(block)
        remaining -= block.height
    if len(columns) % 2:
        columns.append([])
    total = len(columns) // 2
    if total % 2:
        total += 1
    for page_number in range(total):
        top = FIRST_PAGE_TOP if page_number == 0 else LATER_PAGE_TOP
        for side in range(2):
            index = page_number * 2 + side
            column = columns[index] if index < len(columns) else []
            if not column:
                continue
            leftover = (top - BOTTOM_MARGIN) - sum(b.height for b in column)
            share = max(leftover, 0) / len(column)
            x = LEFT_MARGIN + side * (TWO_COLUMN_WIDTH + TWO_COLUMN_GAP)
            y = top
            for block in column:
                draw_block(canvas, block, x, y)
                y -= block.height + share
        canvas.setStrokeColor(colors.lightgrey)
        canvas.setLineWidth(0.5)
        canvas.line(PAGE_WIDTH / 2, BOTTOM_MARGIN, PAGE_WIDTH / 2, top)
        canvas.setStrokeColor(colors.black)
        draw_footer(canvas, page_number + 1, total)
        if page_number + 1 < total:
            canvas.showPage()
    return total


def build_pdf(output_path: Path, source_page: Path = SOURCE_PAGE, title: str | None = None) -> int:
    """Create one printable, questions-only worksheet. Returns the number of questions."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output_path), pagesize=letter)
    lesson_title = WORKSHEET_TITLE_OVERRIDES.get(source_page, title or page_title(source_page))
    canvas.setTitle(f"{lesson_title} Practice Questions")
    canvas.setAuthor("Physics Notes")
    items = practice_items(source_page)

    canvas.setFont(FONT, 15)
    canvas.drawString(LEFT_MARGIN, PAGE_HEIGHT - 0.8 * inch, f"{lesson_title.lower()} - practice problems")
    canvas.setFont(FONT, 10)
    canvas.drawRightString(RIGHT_MARGIN, PAGE_HEIGHT - 0.8 * inch, "name ______________________")

    if source_page == UNITS_SOURCE_PAGE:
        build_units_two_column_pdf(canvas, items, lesson_title)
        canvas.save()
        return len(items)

    pages = layout(items)
    total = len(pages)
    for page_number, page in enumerate(pages):
        y = FIRST_PAGE_TOP if page_number == 0 else LATER_PAGE_TOP
        for block in page:
            draw_block(canvas, block, LEFT_MARGIN, y)
            y -= block.height
        draw_footer(canvas, page_number + 1, total)
        if page_number + 1 < total:
            canvas.showPage()
    canvas.save()
    return len(items)


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
