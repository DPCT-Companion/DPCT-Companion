from unittest import TestCase

from warning_fixer.Plugins.DPCT1015 import DPCT1015
from warning_fixer.SourceFile import SourceFile


class TestDPCT1015(TestCase):
    def test_fix1015(self):
        file = SourceFile("../../test_resources/DPCT1015.dp.cpp", "../../test_resources/DPCT1015.cu", {})
        fixer = DPCT1015(file.lines, "printf(\"assert: lhs=%d, rhs=%d\\n\", x, y);")
        fixer.fix(0, 2)
        self.assertEqual(file.lines[0].line, 'stream_ct1 << "assert: lhs=" << x << ", rhs=" << y << "\\n";')
