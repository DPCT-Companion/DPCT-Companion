import logging
import re
import sys

from warning_fixer.CUDAFile import CUDAFile
from warning_fixer.Plugins.DPCT1003 import DPCT1003
from warning_fixer.Plugins.DPCT1015 import DPCT1015
from warning_fixer.Plugins.DPCT1023 import DPCT1023
from warning_fixer.Plugins.DPCT1065 import DPCT1065
from warning_fixer.SourceLine import SourceLine


class SourceFile:
    def __init__(self, dpcpp_path, cuda_path, cuda_warning_map):
        """
        :param dpcpp_path: the path of dpcpp source file
        :param cuda_path: the path of related cuda file
        :param cuda_warning_map: the map of warnings in the cuda file
        {
            key: DPCT warning code : warning no, e.g. DPCT1015:23
            value: line no in the cuda file
        }
        this value is parsed from the following format in the log of dpct:
        /path/to/cuda/file/cuda_example.cu:126:21: warning: DPCT1015:23:...
        In this example, cuda_warning_map = {"DPCT1015:23": 126}
        """
        self.path = dpcpp_path
        with open(dpcpp_path, "r") as f:
            lines = f.readlines()
        self.lines = []
        for i, l in enumerate(lines):
            self.lines.append(SourceLine(i, l))
        self.cuda_file = CUDAFile(cuda_path)
        self.warning_map = cuda_warning_map

    def get_next_warning(self, begin=0):
        for i, line in enumerate(self.lines[begin:]):
            if line.warning_code:
                start, end = self.get_warning_range(begin + i)
                return line.warning_code, start, end, line.warning_no
        return "", -1, -1, ""

    def get_warning_range(self, index):
        regex_start = re.compile(r"/\*")
        regex_end = re.compile(r"\*/")
        start, end = -1, -1
        for i in range(index, -1, -1):
            if regex_start.search(self.lines[i].line):
                start = i
                break
        for i in range(index+1, len(self.lines)):
            if regex_end.search(self.lines[i].line):
                end = i
                break
        return start, end

    def fix_warnings(self):
        begin = 0
        while True:
            code, start, end, lineno = self.get_next_warning(begin=begin)
            if code == "" or start == -1 or end == -1:
                break
            if code == "DPCT1003":
                fixer = DPCT1003(self.lines)
                fixer.fix(start, end)
                self.lines = fixer.source_lines
                begin = start + 1

            elif code == "DPCT1015":
                key = code + ":" + lineno
                if key not in self.warning_map:
                    logging.error("Cannot find warning", key, "in file", self.path)
                cuda_statement = self.cuda_file.get_statement_from_line_no(self.warning_map[key])
                fixer = DPCT1015(self.lines, cuda_statement)
                fixer.fix(start, end)
                begin = start + 1

            elif code == "DPCT1023":
                key = code + ":" + lineno
                if key not in self.warning_map:
                    logging.error("Cannot find warning", key, "in file", self.path)
                cuda_statement = self.cuda_file.get_statement_from_line_no(self.warning_map[key])
                fixer = DPCT1023(self.lines, cuda_statement)
                fixer.fix(start, end)
                begin = start + 1

            elif code == "DPCT1065":
                fixer = DPCT1065(self.lines)
                fixer.fix(start, end)
                self.lines = fixer.source_lines
                begin = start + 1

            else:
                begin += 1
