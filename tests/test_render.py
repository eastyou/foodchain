"""食物链渲染测试。"""

import unittest

from foodchain.model import FoodChainError, FoodChainProblem, generate_problems
from foodchain.render import render_worksheet


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = generate_problems(6, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_cards(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="card"'), 6)

    def test_no_answers(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 7)

    def test_answer_values(self):
        page = render_worksheet(self.items, answers=True)
        for item in self.items:
            self.assertIn(item.answer, page)

    def test_custom_title(self):
        page = render_worksheet(self.items, title="二班食物链")
        self.assertIn("二班食物链", page)

    def test_empty(self):
        with self.assertRaises(FoodChainError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(FoodChainError):
            render_worksheet(["草"])

    def test_prompts(self):
        page = render_worksheet(self.items)
        for item in self.items:
            self.assertIn(item.prompt, page)

    def test_escaping(self):
        page = render_worksheet(self.items, title="A&B")
        self.assertIn("A&amp;B", page)

    def test_single_item(self):
        page = render_worksheet([FoodChainProblem("兔", "predator")], answers=True)
        self.assertIn("狐", page)


if __name__ == "__main__":
    unittest.main()
