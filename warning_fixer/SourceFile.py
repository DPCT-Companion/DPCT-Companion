import logging
import re
import sys

from warning_fixer.Plugins.DPCT1003 import DPCT1003
from warning_fixer.SourceLine import SourceLine


class SourceFile:
    def __init__(self, path):
        with open(path, "r") as f:
            lines = f.readlines()
        self.lines = []
        for i, l in enumerate(lines):
            self.lines.append(SourceLine(i, l))

    def get_next_warning(self, begin=0):
        for i, line in enumerate(self.lines[begin:]):
            if line.warning_code:
                start, end = self.get_warning_range(begin + i)
                return line.warning_code, start, end
        return "", -1, -1

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
            code, start, end = self.get_next_warning(begin=begin)
            if code == "" or start == -1 or end == -1:
                break
            if code == "DPCT1003":
                fixer = DPCT1003(self.lines)
                fixer.fix(start, end)
                self.lines = fixer.source_lines
                begin = start + 1
