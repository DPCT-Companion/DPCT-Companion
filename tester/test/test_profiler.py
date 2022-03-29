import unittest

from tester.Profile import *


class ProfilerTest(unittest.TestCase):
    def test_profiler(self):
        # TODO: We need a CUDA / DPC++ application which actually used the GPU here.
        result = profile("a.out", "b.out", 1200)

        self.assertIsInstance(result["cuda_gpu_time"], float)
        self.assertIsInstance(result["cuda_gpu_sm_active"], float)
        self.assertGreater(result["cuda_gpu_time"], 0.0)

        self.assertIsInstance(result["dpcpp_gpu_time"], float)
        self.assertIsInstance(result["dpcpp_gpu_eu_active"], float)
        self.assertGreater(result["dpcpp_gpu_time"], 0.0)


if __name__ == '__main__':
    unittest.main()
