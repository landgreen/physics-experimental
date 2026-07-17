"""Checks for the Motion practice worksheet generator."""

import unittest

from generate_motion_practice_pdf import choose_workspace_extra_lines, page_count, practice_questions


class PracticeQuestionTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
