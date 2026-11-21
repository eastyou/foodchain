"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from foodchain.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_chains(self):
        code, out, _ = run(["chains"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 7)
        self.assertIn("草 → 兔 → 狐", out)

    def test_show(self):
        code, out, _ = run(["show", "海洋"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 2)
        self.assertIn("鲨鱼", out)

    def test_show_unknown(self):
        code, _, err = run(["show", "沙漠"])
        self.assertEqual(code, 2)
        self.assertIn("未知生态系统", err)

    def test_role_producer(self):
        code, out, _ = run(["role", "草"])
        self.assertEqual(code, 0)
        self.assertIn("生产者", out)

    def test_role_consumer(self):
        code, out, _ = run(["role", "兔"])
        self.assertEqual(code, 0)
        self.assertIn("消费者", out)

    def test_role_unknown(self):
        code, _, err = run(["role", "恐龙"])
        self.assertEqual(code, 2)
        self.assertIn("未知生物", err)

    def test_predator(self):
        code, out, _ = run(["predator", "兔"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "狐")

    def test_predator_none(self):
        code, out, _ = run(["predator", "狐"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "没有天敌")

    def test_prey(self):
        code, out, _ = run(["prey", "蛇"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "鼠、蛙、松鼠")

    def test_prey_none(self):
        code, out, _ = run(["prey", "草"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "不吃别的生物")

    def test_check_ok(self):
        code, out, _ = run(["check", "草", "兔", "狐"])
        self.assertEqual(code, 0)
        self.assertIn("是一条已知食物链", out)

    def test_check_fail(self):
        code, out, _ = run(["check", "狐", "兔", "草"])
        self.assertEqual(code, 1)
        self.assertIn("不是已知食物链", out)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_ecosystem(self):
        code, out, _ = run(
            ["sheet", "--count", "4", "--ecosystem", "森林", "--seed", "3"]
        )
        self.assertEqual(code, 0)
        self.assertNotIn("鲨鱼", out)
        self.assertNotIn("海獭", out)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_bad_ecosystem(self):
        code, _, err = run(["sheet", "--ecosystem", "沙漠"])
        self.assertEqual(code, 2)
        self.assertIn("未知生态系统", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "9999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
