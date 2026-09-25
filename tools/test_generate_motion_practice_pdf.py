"""Checks for the practice worksheet generator."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import fitz  # pymupdf

from generate_motion_practice_pdf import (
    ROOT,
    build_all_pdfs,
    build_pdf,
    practice_items,
    practice_pages,
    practice_questions,
)


class PracticeWorksheetTests(unittest.TestCase):
    def test_finds_every_notes_page_with_a_practice_section(self) -> None:
        pages = practice_pages()
        slugs = {page.slug for page in pages}
        self.assertIn("motion", slugs)
        self.assertIn("kinematics", slugs)
        self.assertIn("electricity", slugs)
        self.assertTrue(all(page.questions for page in pages))
        self.assertEqual(len(slugs), len(pages))

    def test_extracts_examples_without_the_reading_card(self) -> None:
        questions = practice_questions()
        self.assertEqual(len(questions), 17)
        self.assertIn("Two cars drive toward each other", questions[-1])
        self.assertFalse(any("Reading" in question for question in questions))

    def test_skips_cards_marked_printout_ignore(self) -> None:
        source = ROOT / "notes/circuits/kirchoff/index.html"
        page_html = source.read_text(encoding="utf-8")
        ignored = page_html.count("example printout-ignore")
        self.assertGreater(ignored, 0)
        prompts = practice_questions(source)
        self.assertFalse(any("A battery raises charge from 0.0 V to 12.0 V" in prompt for prompt in prompts))

    def test_keeps_superscripts_as_superscripts(self) -> None:
        items = practice_items(ROOT / "notes/waves/quantum/index.html")
        markup = next(item.markup for item in items if "5.60" in item.markup)
        self.assertIn("10<super>14</super>", markup)

    def test_keeps_quantum_reference_table_out_of_the_printout_prompt(self) -> None:
        items = practice_items(ROOT / "notes/waves/quantum/index.html")
        item = next(item for item in items if "n = 3 energy level" in item.text)
        self.assertEqual(item.tables, [])
        self.assertIn('<table class="printout-ignore">', (ROOT / "notes/waves/quantum/index.html").read_text(encoding="utf-8"))

    def test_circuit_diagrams_travel_with_their_questions(self) -> None:
        items = practice_items(ROOT / "notes/circuits/kirchoff/index.html")
        diagram_items = [item for item in items if item.svg]
        self.assertGreater(len(diagram_items), 0)
        self.assertTrue(all("above" not in item.text for item in diagram_items))

    def test_every_worksheet_fills_one_or_two_double_sided_sheets(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            generated = build_all_pdfs(output_directory)
            self.assertEqual(len(generated), len(practice_pages()))
            for page in practice_pages():
                pdf_path = output_directory / f"{page.slug}-practice-questions.pdf"
                document = fitz.open(pdf_path)
                self.assertIn(document.page_count, (2, 4), page.slug)
                text = "".join(p.get_text() for p in document)
                self.assertIn("practice problems", text)
                self.assertNotIn("\\frac", text)  # no solution math leaked in
                self.assertNotIn("$$", text)

    def test_names_the_momentum_conservation_worksheet(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            pdf_path = Path(temporary_directory) / "momentum-conservation-practice-questions.pdf"
            build_pdf(pdf_path, ROOT / "notes/momentum/conservation/index.html")
            first_page = fitz.open(pdf_path)[0].get_text()
            self.assertIn("momentum conservation - practice problems", first_page)


if __name__ == "__main__":
    unittest.main()
