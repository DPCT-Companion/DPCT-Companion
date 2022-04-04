from pathlib import Path
from unittest import TestCase

from warning_fixer.SourceProject import SourceProject


class TestSourceProject(TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).resolve().parent.joinpath("test_resources").joinpath("test_project")
        self.dpcpp_root_path = self.path.joinpath("dpcpp")
        self.cuda_root_path = self.path.joinpath("cuda")
        self.output_path = self.path.joinpath("migrated")
        self.log_path = self.path.joinpath("dpct.log")

    def test_source_project(self):
        project = SourceProject(self.dpcpp_root_path,
                                self.cuda_root_path,
                                self.output_path,
                                self.log_path)
        project.fix_project_warnings()
