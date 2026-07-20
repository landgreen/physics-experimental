"""Checks for the Motion practice worksheet generator."""

import unittest
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pdfplumber
from pypdf import PdfReader

from generate_motion_practice_pdf import (
    build_all_pdfs,
    build_pdf,
    choose_workspace_extra_lines,
    page_count,
    practice_pages,
    practice_questions,
    workspace_extra_lines,
)


class PracticeQuestionTests(unittest.TestCase):

    def test_finds_every_notes_page_with_a_practice_section(self) -> None:
        pages = practice_pages()

        self.assertEqual(len(pages), 27)
        self.assertIn("motion", {page.slug for page in pages})
        self.assertIn("kinematics", {page.slug for page in pages})
        self.assertIn("electricity", {page.slug for page in pages})
        self.assertTrue(all(page.questions for page in pages))
        self.assertEqual(len({page.slug for page in pages}), len(pages))

    def test_extracts_examples_without_the_reading_card(self) -> None:
        questions = practice_questions()

        self.assertEqual(len(questions), 17)
        self.assertIn("Two cars drive toward each other", questions[-1])
        self.assertFalse(any("Reading (5 minutes)" in question for question in questions))

    def test_uses_extra_space_without_exceeding_the_even_page_target(self) -> None:
        questions = practice_questions()
        extra_lines = choose_workspace_extra_lines(questions)

        self.assertGreater(extra_lines, 0)
        self.assertEqual(page_count(questions, extra_lines), 4)

    def test_uses_an_even_number_of_pages_for_each_worksheet(self) -> None:
        for page in practice_pages():
            extra_lines = workspace_extra_lines(list(page.questions))

            self.assertEqual(len(extra_lines), len(page.questions))
            self.assertEqual(page_count(list(page.questions), extra_lines) % 2, 0)

    def test_generates_a_questions_only_pdf_for_each_practice_section(self) -> None:
        with TemporaryDirectory() as directory:
            output_directory = Path(directory)
            generated = build_all_pdfs(output_directory)

            self.assertEqual(len(generated), 27)
            for page in practice_pages():
                pdf_path = output_directory / f"{page.slug}-practice-questions.pdf"
                self.assertTrue(pdf_path.is_file())
                text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
                self.assertIn(page.title.lower(), text.lower())
                if page.slug == "motion":
                    self.assertNotIn("At the meeting time, both trains have the same position.", text)

    def test_compacts_units_into_four_pages(self) -> None:
        units_page = next(page for page in practice_pages() if page.slug == "units")

        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "units-practice-questions.pdf"
            build_pdf(pdf_path, source_page=units_page.source, title=units_page.title)

            reader = PdfReader(pdf_path)
            self.assertEqual(len(reader.pages), 4)
            final_page = reader.pages[3].extract_text() or ""
            self.assertIn("31. You walk 50 m northeast.", final_page)
            self.assertIn("35. A long spacecraft tracking distance", final_page)
            self.assertNotIn("30. A plane is moving 20 m/s", final_page)

            with pdfplumber.open(pdf_path) as pdf:
                column_counts = []
                for page in pdf.pages:
                    labels = [word for word in page.extract_words() if re.fullmatch(r"\d+\.", word["text"])]
                    left = sum(word["x0"] < page.width / 2 for word in labels)
                    column_counts.append((left, len(labels) - left))
                self.assertEqual(column_counts, [(5, 5), (5, 5), (5, 5), (3, 2)])

    def test_names_the_momentum_conservation_worksheet(self) -> None:
        conservation_page = next(page for page in practice_pages() if page.slug == "momentum-conservation")

        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "momentum-conservation-practice-questions.pdf"
            build_pdf(pdf_path, source_page=conservation_page.source, title=conservation_page.title)

            heading = (PdfReader(pdf_path).pages[0].extract_text() or "").splitlines()[0]
            self.assertEqual(heading, "momentum conservation - practice problems")


if __name__ == "__main__":
    unittest.main()
