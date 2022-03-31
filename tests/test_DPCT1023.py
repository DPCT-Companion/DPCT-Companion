import unittest
from pathlib import Path

from warning_fixer.Plugins.DPCT1023 import DPCT1023
from warning_fixer.SourceFile import SourceFile


class DPCT1023Test(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parent.joinpath("test_resources")

    def test_normalize(self):
        file = SourceFile(str(self.path.joinpath("DPCT1023.dp.cpp")), str(self.path.joinpath("DPCT1023.cu")), {})
        testcase = DPCT1023(file.lines, "        uint32_t x = __shfl_up_sync(warp_mask, carry, 1);", 0, 0)
        testcase.dpcxx_code_line = "        uint32_t x =\n            sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);"
        testcase.normalize_input()
        self.assertEqual(testcase.cuda_code_line, "uint32_t x = __shfl_up_sync(warp_mask, carry, 1);")
        self.assertEqual(testcase.dpcxx_code_line,
                         "uint32_t x = sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);")

    def test_variable(self):
        file = SourceFile(str(self.path.joinpath("DPCT1023.dp.cpp")), str(self.path.joinpath("DPCT1023.cu")), {})
        testcase = DPCT1023(file.lines, "        uint32_t x = __shfl_up_sync(warp_mask, carry, 1);", 0, 3)
        testcase.fix()
        truth = "x = carry;\nsycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & warp_mask)\n{\n    uint32_t x = sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);\n}\n"
        self.assertListEqual([l.line for l in testcase.source_lines[:7]], truth.splitlines(True))

    def test_fullmask(self):
        file = SourceFile(str(self.path.joinpath("DPCT1023.dp.cpp")), str(self.path.joinpath("DPCT1023.cu")), {})
        testcase = DPCT1023(file.lines, "const int32_t mv = __shfl_down_sync(0xffff'ffffu, cur_min, i);", 8, 11)
        testcase.fix()
        self.assertEqual(testcase.source_lines[8].line,
                         "        const int32_t mv = sycl::shift_group_left(item_ct1.get_sub_group(), cur_min, i);\n")
