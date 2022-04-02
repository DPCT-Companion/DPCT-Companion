import subprocess
import unittest
from pathlib import Path

from tester.Checker import check_all
from tester.Test import *


class TestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = str(Path(__file__).resolve().parent.joinpath("test_resources"))
        subprocess.run(["g++", f"{self.path}/a.cpp", "-o", f"{self.path}/a.out"], check=True)
        subprocess.run(["g++", f"{self.path}/b.cpp", "-o", f"{self.path}/b.out"], check=True)

    def test_test_success(self):
        steps = [{'input-stdin': {'key': 42, 'omit-newline': False}}, {'sleep': 1},
                 {'check-stdout': {'name': 'check1', 'omit-line': [2]}}]
        args = ["arg1", "arg2"]
        case = {"args": args, "steps": steps}
        cuda_result, dpcpp_result = do_test([case], f"{self.path}/a.out", f"{self.path}/b.out", "cuda,dpcpp")
        r = check_all([{"steps": steps}], cuda_result, dpcpp_result)
        self.assertTrue(r[0][0].pass_check)


if __name__ == '__main__':
    unittest.main()
