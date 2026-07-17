"""Checks for the Motion practice worksheet generator."""

import unittest

from generate_motion_practice_pdf import practice_questions


class PracticeQuestionTests(unittest.TestCase):
    def test_extracts_examples_without_the_reading_card(self) -> None:
        questions = practice_questions()

        self.assertEqual(len(questions), 17)
        self.assertIn("Two cars drive toward each other", questions[-1])
        self.assertFalse(any("Reading (5 minutes)" in question for question in questions))


if __name__ == "__main__":
    unittest.main()
