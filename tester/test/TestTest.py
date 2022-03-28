import unittest
from os.path import *
from tester.Test import *
import subprocess

path = dirname(realpath(__file__))
subprocess.run(["g++", f"{path}/a.cpp", "-o", f"{path}/a.out"], check=True)
subprocess.run(["g++", f"{path}/b.cpp", "-o", f"{path}/b.out"], check=True)


class TestTest(unittest.TestCase):
    def test_test_success(self):
        case = [{'input-stdin': {'key': 42, 'omit-newline': False}}, {'sleep': 1},
                {'check-stdout': {'name': 'check1', 'omit-line': [2]}}]
        print(case)
        r = test([case], f"{path}/a.out", f"{path}/b.out")
        self.assertTrue(r[0][0].pass_check)


if __name__ == '__main__':
    unittest.main()
