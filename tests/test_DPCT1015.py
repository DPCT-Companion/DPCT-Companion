from pathlib import Path
from unittest import TestCase

from warning_fixer.Plugins.DPCT1015 import DPCT1015
from warning_fixer.SourceFile import SourceFile


class TestDPCT1015(TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parent.joinpath("test_resources")

    def test_fix1015(self):
        file = SourceFile(str(self.path.joinpath("DPCT1015.dp.cpp")), str(self.path.joinpath("DPCT1015.cu")), {})
        fixer = DPCT1015(file.lines, "printf(\"assert: lhs=%d, rhs=%d\\n\", x, y);", 0, 2)
        fixer.fix()
        self.assertEqual(file.lines[0].line, 'stream_ct1 << "assert: lhs=" << x << ", rhs=" << y << "\\n";\n')
