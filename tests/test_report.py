import unittest
from os.path import *
from tester.parse import *
from tester.Checker import Checker


class TestReport(unittest.TestCase):
    def test_report(self):
        a = Checker("hello", "hello world!!", name="check 1", c1=0)
        self.assertFalse(a.pass_check)
        b = Checker("i love python\nme too!", "i love java\nme too!", name="check 2", c1=0)
        self.assertFalse(b.pass_check)
        c = Checker("apple juice", "orange juice", name="check 3", c1=0)
        self.assertFalse(c.pass_check)
        d = Checker("yay!\npass!", "yay!\npass!", name="check 4", c1=0)
        self.assertTrue(d.pass_check)
        checks = [[a, b], [c, d]]
        r = report(checks)
        self.assertRegex(r, "((.|\n)*)Pass: 1((.|\n)*)")
        self.assertRegex(r, "((.|\n)*)Not Matched: 3((.|\n)*)")
        self.assertRegex(r, "((.|\n)*)Crashed: 0((.|\n)*)")


if __name__ == '__main__':
    unittest.main()
