import subprocess
import unittest
from pathlib import Path

from tester.Test import *

path = str(Path(__file__).resolve().parent)
subprocess.run(["g++", f"{path}/a.cpp", "-o", f"{path}/a.out"], check=True)
subprocess.run(["g++", f"{path}/b.cpp", "-o", f"{path}/b.out"], check=True)


class TestTest(unittest.TestCase):
    def test_test_success(self):
        steps = [{'input-stdin': {'key': 42, 'omit-newline': False}}, {'sleep': 1},
                {'check-stdout': {'name': 'check1', 'omit-line': [2]}}]
        args = ["arg1", "arg2"]
        case = {"args": args, "steps": steps}
        r = test([case], f"{path}/a.out", f"{path}/b.out")
        self.assertTrue(r[0][0].pass_check)


if __name__ == '__main__':
    unittest.main()
