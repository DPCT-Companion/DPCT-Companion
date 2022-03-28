import unittest
from os.path import *
from copy import copy
from tester.Build import *

path = dirname(realpath(__file__))
std_config = {"cuda-exec": f"{path}/a.out", "dpcpp-exec": f"{path}/b.out",
              "cuda-script": f"g++ {path}/a.cpp -o {path}/a.out", "dpcpp-script": f"g++ {path}/b.cpp -o {path}/b.out"}


class BuildTest(unittest.TestCase):
    def test_build_success(self):
        self.assertEqual(build(std_config), (f"{path}/a.out", f"{path}/b.out"))

    def test_build_success_without_script(self):
        config = copy(std_config)
        del (config["cuda-script"])
        del(config["dpcpp-script"])
        self.assertEqual(build(std_config), (f"{path}/a.out", f"{path}/b.out"))

    def test_no_cuda_exec(self):
        config = copy(std_config)
        del(config["cuda-exec"])

        def _build():
            build(config)
        self.assertRaises(Exception, _build, msg="fail: no build.cuda-exec")

    def test_no_dpcpp_exec(self):
            config = copy(std_config)
            del (config["dpcpp-exec"])

            def _build():
                build(config)

            self.assertRaises(Exception, _build, msg="fail: no build.dpcpp-exec")

    def test_bad_cuda_format(self):
        config = copy(std_config)
        config["cuda-exec"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-exec should be a string")

    def test_bad_dpcpp_format(self):
        config = copy(std_config)
        config["dpcpp-exec"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-dpcpp should be a string")

    def test_bad_cuda_script_format(self):
        config = copy(std_config)
        config["cuda-script"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.cuda-script should be a string")

    def test_bad_dpcpp_script_format(self):
        config = copy(std_config)
        config["cuda-script"] = 42

        def _build():
            build(config)

        self.assertRaises(Exception, _build, msg="fail: build.dpcpp-script should be a string")


if __name__ == '__main__':
    unittest.main()
