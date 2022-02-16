from unittest import TestCase

from warning_fixer.SourceFile import SourceFile


class TestDPCT1003(TestCase):
    def test_fix1003(self):
        file = SourceFile("../../test_resources/DPCT1003.dp.cpp")
        file.fix_warnings()
        self.assertEqual(file.lines[2].line, '        ptr = (void *)sycl::malloc_device(n * sizeof(T),dpct::get_default_queue());\n')
        self.assertEqual(file.lines[4].line, '        ptr = (void *)sycl::malloc_device(n * sizeof(T),dpct::get_default_queue());\n')