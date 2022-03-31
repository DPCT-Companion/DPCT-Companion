import unittest
from pathlib import Path

from tester.Build import *


class BuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = str(Path(__file__).resolve().parent.joinpath("test_resources"))
        self.std_config = {"cuda-exec": f"{self.path}/a.out", "dpcpp-exec": f"{self.path}/b.out",
                      "cuda-script": f"g++ {self.path}/a.cpp -o {self.path}/a.out",
                      "dpcpp-script": f"g++ {self.path}/b.cpp -o {self.path}/b.out"}

    def test_build_success(self):
        self.assertEqual(build(self.std_config, "cuda,dpcpp"), (f"{self.path}/a.out", f"{self.path}/b.out"))

    def test_build_success_without_script(self):
        config = self.std_config
        del (config["cuda-script"])
        del(config["dpcpp-script"])
        self.assertEqual(build(self.std_config, "cuda,dpcpp"), (f"{self.path}/a.out", f"{self.path}/b.out"))

    def test_no_cuda_exec(self):
        config = self.std_config
        del(config["cuda-exec"])

        def _build():
            build(config, "cuda,dpcpp")
        self.assertRaises(Exception, _build, msg="fail: no build.cuda-exec")
        self.assertEqual(build(config, "dpcpp"), ("", f"{self.path}/b.out"))

    def test_no_dpcpp_exec(self):
        config = self.std_config
        del (config["dpcpp-exec"])

        def _build():
            build(config, "cuda,dpcpp")

        self.assertRaises(Exception, _build, msg="fail: no build.dpcpp-exec")
        self.assertEqual(build(config, "cuda"), (f"{self.path}/a.out", ""))

    def test_bad_cuda_format(self):
        config = self.std_config
        config["cuda-exec"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-exec should be a string")

    def test_bad_dpcpp_format(self):
        config = self.std_config
        config["dpcpp-exec"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-dpcpp should be a string")

    def test_bad_cuda_script_format(self):
        config = self.std_config
        config["cuda-script"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-script should be a string")

    def test_bad_dpcpp_script_format(self):
        config = self.std_config
        config["cuda-script"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.dpcpp-script should be a string")


if __name__ == '__main__':
    unittest.main()
