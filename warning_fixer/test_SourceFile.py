from unittest import TestCase

from warning_fixer.SourceFile import SourceFile


class TestSourceFile(TestCase):
    def test_1003_fix_one_file(self):
        source_file = SourceFile("../test_resources/cudapoa_batch.dp.hpp")
        source_file.fix_warnings()
        lines = "".join([line.line for line in source_file.lines])
        with open("../test_resources/cudapoa_batch_new.dp.hpp", "w") as f:
            f.write(lines)