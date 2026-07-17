"""Checks for the Motion practice worksheet generator."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pypdf import PdfReader

from generate_motion_practice_pdf import (
    build_all_pdfs,
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


if __name__ == "__main__":
    unittest.main()
