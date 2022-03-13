from unittest import TestCase

from warning_fixer.Plugins.DPCT1003 import DPCT1003
from warning_fixer.SourceFile import SourceFile


class TestDPCT1003(TestCase):
    def test_fix1003(self):
        file = SourceFile("../../test_resources/DPCT1003.dp.cpp", "", {})
        fixer = DPCT1003(file.lines, 18, 21)
        fixer.fix()
        self.assertEqual(file.lines[18].line, '        ptr = (void *)sycl::malloc_device(n * sizeof(T), dpct::get_default_queue());\n')

    def test_fix1003_multiple(self):
        file = SourceFile("../../test_resources/DPCT1003.dp.cpp", "", {})
        file.fix_warnings()
        self.assertTrue("DPCT1007:15" in file.lines[3].line)
        self.assertEqual(file.lines[6].line, '        ptr = (void *)sycl::malloc_device(n * sizeof(T), dpct::get_default_queue());\n')
        print("".join([l.line for l in file.lines]))

    def test_fix1003_with_try(self):
        file = SourceFile("../../test_resources/DPCT1003_trycatch.dp.cpp", "", {})
        file.fix_warnings()
        self.assertEqual(file.lines[6].line, 66 * ' ' + 'try {sycl::free(ptr,dpct::get_default_queue());\n')