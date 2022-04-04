from pathlib import Path
from unittest import TestCase

from warning_fixer.Plugins.DPCT1065 import DPCT1065
from warning_fixer.SourceFile import SourceFile


class TestDPCT1065(TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parent.joinpath("test_resources")

    def test_fix1065(self):
        file = SourceFile(str(self.path.joinpath("DPCT1065.dp.cpp")), "", {})
        fixer = DPCT1065(file.lines, 2, 6)
        fixer.fix()
        self.assertEqual(file.lines[2].line, '    item_ct1.barrier(sycl::access::fence_space::local_space);\n')
