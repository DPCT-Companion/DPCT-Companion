import os
import subprocess
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tester.Profile import *
from tester.parse import parse


class ProfilerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parent.joinpath("test_resources").joinpath("test_harness_project")
        self.cuda_path = self.path.joinpath("cuda")
        self.dpcpp_path = self.path.joinpath("dpcpp")
        try:
            subprocess.run(["dpcpp", "-v"], check=True)
            self.has_dpcpp = True
        except Exception:
            self.has_dpcpp = False
        try:
            subprocess.run(["nvcc", "-v"], check=True)
            self.has_cuda = True
        except Exception:
            self.has_cuda = False
        try:
            subprocess.run(["vtune", "--version"], check=True)
            self.has_vtune = True
        except Exception:
            self.has_vtune = False
        try:
            subprocess.run(["ncu"], check=True)
            self.has_ncu = True
        except Exception:
            self.has_ncu = False

    def test_profiler(self):
        os.chdir(self.path)
        config, test_cases = parse(self.path.joinpath("build.yml"))
        result_cuda = profile_cuda(str(self.cuda_path.joinpath("stencil_1d")), test_cases, 1200)
        result_dpcpp = profile_dpcpp(str(self.dpcpp_path.joinpath("main")), test_cases, 1200)

        self.assertIsInstance(result_cuda[0]["cuda_gpu_time"], float)
        self.assertIsInstance(result_cuda[0]["cuda_gpu_sm_active"], float)
        if self.has_ncu:
            self.assertGreater(result_cuda[0]["cuda_gpu_time"], 0.0)
        else:
            self.assertEqual(result_cuda[0]["cuda_gpu_time"], 0.0)

        self.assertIsInstance(result_dpcpp[0]["dpcpp_gpu_time"], float)
        self.assertIsInstance(result_dpcpp[0]["dpcpp_gpu_eu_active"], float)
        if self.has_vtune:
            self.assertGreater(result_dpcpp[0]["dpcpp_gpu_time"], 0.0)
        else:
            self.assertEqual(result_dpcpp[0]["dpcpp_gpu_time"], 0.0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_profiler_dpcpp(self, stdout):
        if not self.has_dpcpp or not self.has_vtune:
            return
        os.chdir(self.path)
        config, test_cases = parse(self.path.joinpath("build.yml"))
        profile(config, test_cases, "dpcpp", 1200)
        print(stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
