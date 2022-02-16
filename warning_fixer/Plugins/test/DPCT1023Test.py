import unittest
from DPCT1023 import *

class DPCT1023Test(unittest.TestCase):

    def test_normalize(self):
        testcase = DPCT1023("        uint32_t x = __shfl_up_sync(warp_mask, carry, 1);", "        uint32_t x =\n            sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);")
        testcase.normalize_input()
        self.assertEqual(testcase.cuda_code_line, "uint32_t x = __shfl_up_sync(warp_mask, carry, 1);")
        self.assertEqual(testcase.dpcxx_code_line, "uint32_t x = sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);")

    def test_variable(self):
        testcase = DPCT1023("uint32_t x = __shfl_up_sync(warp_mask, carry, 1);", "uint32_t x = sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);")
        result = testcase.fix()
        self.assertEqual(result, "sycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & warp_mask)\n{{\n    uint32_t x = sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);\n}}\n")

    def test_fullmask(self):
        testcase = DPCT1023("const int32_t mv = __shfl_down_sync(0xffff'ffffu, cur_min, i);", "const int32_t mv = sycl::shift_group_left(item_ct1.get_sub_group(), cur_min, i);")
        result = testcase.fix()
        self.assertEqual(result, "sycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & 0xffff'ffffu)\n{{\n    const int32_t mv = sycl::shift_group_left(item_ct1.get_sub_group(), cur_min, i);\n}}\n")