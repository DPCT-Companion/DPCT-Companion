import unittest

from tester.Profile import *


class ProfilerTest(unittest.TestCase):
    def test_profiler(self):
        # TODO: We need a CUDA / DPC++ application which actually used the GPU here.
        result_cuda = profile_cuda("cuda_prof_test", None, 1200)
        result_dpcpp = profile_dpcpp("dpcpp_prof_test", None, 1200)

        self.assertIsInstance(result_cuda["cuda_gpu_time"], float)
        self.assertIsInstance(result_cuda["cuda_gpu_sm_active"], float)
        self.assertGreater(result_cuda["cuda_gpu_time"], 0.0)

        self.assertIsInstance(result_dpcpp["dpcpp_gpu_time"], float)
        self.assertIsInstance(result_dpcpp["dpcpp_gpu_eu_active"], float)
        self.assertGreater(result_dpcpp["dpcpp_gpu_time"], 0.0)


if __name__ == '__main__':
    unittest.main()
