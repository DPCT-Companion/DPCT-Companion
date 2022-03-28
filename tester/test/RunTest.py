import unittest
from os.path import *
from tester.run import *
from tester.Test import Check


class RunTest(unittest.TestCase):
    def test_report(self):
        a = Check("hello", "hello world!!", name="check 1", c1=0)
        a.pass_check = False
        b = Check("i love python\nme too!", "i love java\nme too!", name="check 2", c1=0)
        b.pass_check = False
        c = Check("apple juice", "orange juice", name="check 3", c1=0)
        c.pass_check = False
        d = Check("yay!\npass!", "yay!\npass!", name="check 4", c1=0)
        d.pass_check = True
        checks = [[a, b], [c, d]]
        r = report(checks)
        self.assertRegex(r, "((.|\n)*)Pass: 1((.|\n)*)")
        self.assertRegex(r, "((.|\n)*)Not Matched: 3((.|\n)*)")
        self.assertRegex(r, "((.|\n)*)Crashed: 0((.|\n)*)")


if __name__ == '__main__':
    unittest.main()
