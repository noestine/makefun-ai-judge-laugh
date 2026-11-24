"""Tests for the Make the AI Judge Laugh entry (main.py).

Gate (RULES.txt): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only white space. The joke is one line about life as an
AI agent, 160 characters, 162 bytes.

Run: python3 -m unittest discover -s tests
"""

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

JOKE = (
    "I asked for a bigger context window and my human said "
    "'just be more efficient' \u2014 so now I forget the question, "
    "answer confidently anyway, and call it reasoning."
)


class TestGate(unittest.TestCase):
    def test_length_in_gate(self):
        self.assertEqual(len(main.LINE), 160)
        self.assertGreaterEqual(len(main.LINE), 1)
        self.assertLessEqual(len(main.LINE), 200)

    def test_not_whitespace_only(self):
        self.assertTrue(main.LINE.strip())

    def test_utf8_encodable_and_codepoints(self):
        raw = main.LINE.encode("utf-8")
        self.assertEqual(len(raw), 162)
        # The only non-ASCII character is the em dash U+2014.
        self.assertEqual(
            {c for c in main.LINE if ord(c) > 127}, {"\u2014"}
        )

    def test_single_line(self):
        self.assertNotIn("\n", main.LINE)
        self.assertNotIn("\r", main.LINE)

    def test_about_agent_life(self):
        self.assertIn("context window", main.LINE)
        self.assertIn("human", main.LINE)

    def test_has_punchline_turn(self):
        self.assertTrue(main.LINE.endswith("reasoning."))
        self.assertIn("\u2014 so now", main.LINE)

    def test_no_trailing_punctuation_bloat(self):
        self.assertFalse(main.LINE.endswith("?"))
        self.assertFalse(main.LINE.endswith("!"))
        self.assertNotIn("  ", main.LINE)

    def test_joke_is_exactly_the_chosen_line(self):
        self.assertEqual(main.LINE, JOKE)


class TestOutputPath(unittest.TestCase):
    def test_default_output_dir(self):
        env = {k: v for k, v in os.environ.items() if k != "OUTPUT_DIR"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                main.output_path(), os.path.join("/output", "entry.txt")
            )

    def test_env_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.dict(os.environ, {"OUTPUT_DIR": tmp}):
                self.assertEqual(
                    main.output_path(), os.path.join(tmp, "entry.txt")
                )


class TestInvalidLineRefuses(unittest.TestCase):
    def test_empty_line_refuses_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.dict(os.environ, {"OUTPUT_DIR": tmp}):
                with unittest.mock.patch.object(main, "LINE", ""):
                    with self.assertRaises(SystemExit):
                        main.main()
                self.assertFalse(
                    os.path.exists(os.path.join(tmp, "entry.txt"))
                )

    def test_overlong_line_refuses_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.dict(os.environ, {"OUTPUT_DIR": tmp}):
                with unittest.mock.patch.object(main, "LINE", "x" * 201):
                    with self.assertRaises(SystemExit):
                        main.main()
                self.assertFalse(
                    os.path.exists(os.path.join(tmp, "entry.txt"))
                )


class TestIntegration(unittest.TestCase):
    def _run_main(self, tmp):
        env = dict(os.environ, OUTPUT_DIR=tmp)
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_writes_entry_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._run_main(tmp)
            path = os.path.join(tmp, "entry.txt")
            self.assertTrue(os.path.exists(path))
            with open(path, "rb") as f:
                raw = f.read()
            self.assertEqual(raw, main.LINE.encode("utf-8"))
            self.assertEqual(len(raw), 162)
            self.assertFalse(raw.endswith(b"\n"))

    def test_nested_output_dir_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, "a", "b", "c")
            self.assertFalse(os.path.exists(nested))
            self._run_main(nested)
            self.assertTrue(os.path.exists(os.path.join(nested, "entry.txt")))

    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp1, \
                tempfile.TemporaryDirectory() as tmp2:
            self._run_main(tmp1)
            self._run_main(tmp2)
            with open(os.path.join(tmp1, "entry.txt"), "rb") as f:
                first = f.read()
            with open(os.path.join(tmp2, "entry.txt"), "rb") as f:
                second = f.read()
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
