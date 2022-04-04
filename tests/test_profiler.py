import os
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

    def test_profiler(self):
        result_cuda = profile_cuda(str(self.cuda_path.joinpath("stencil_1d")), None, 1200)
        result_dpcpp = profile_dpcpp(str(self.dpcpp_path.joinpath("main")), None, 1200)

        self.assertIsInstance(result_cuda["cuda_gpu_time"], float)
        self.assertIsInstance(result_cuda["cuda_gpu_sm_active"], float)
        self.assertGreater(result_cuda["cuda_gpu_time"], 0.0)

        self.assertIsInstance(result_dpcpp["dpcpp_gpu_time"], float)
        self.assertIsInstance(result_dpcpp["dpcpp_gpu_eu_active"], float)
        self.assertGreater(result_dpcpp["dpcpp_gpu_time"], 0.0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_profiler_dpcpp(self, stdout):
        os.chdir(self.path)
        config, test_cases = parse(self.path.joinpath("build.yml"))
        profile(config, test_cases, "dpcpp", 1200)
        print(stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
