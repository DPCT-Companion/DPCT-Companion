from unittest import TestCase

from warning_fixer.SourceFile import SourceFile
from warning_fixer.SourceProject import SourceProject


class TestSourceProject(TestCase):
    def test_source_project(self):
        project = SourceProject(dpcpp_root_path="test_resources/test_project/dpcpp",
                                cuda_root_path="test_resources/test_project/cuda",
                                output_path="test_resources/test_project/migrated",
                                log_path="test_resources/test_project/dpct.log")
        project.fix_project_warnings()
