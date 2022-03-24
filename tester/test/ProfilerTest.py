import unittest
from tester.Profile import *


class ProfilerTest(unittest.TestCase):
    def test_profiler(self):
        result = profile("sample_profiler", 1200)
        self.assertIsInstance(result["gpu_time"], float)
        self.assertIsInstance(result["gpu_eu_idle"], float)
        self.assertGreater(result["gpu_time"], 0.0)


if __name__ == '__main__':
    unittest.main()
