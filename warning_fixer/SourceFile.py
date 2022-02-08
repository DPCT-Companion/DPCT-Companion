import logging
import re
import sys

from warning_fixer.SourceLine import SourceLine


class SourceFile:
    def __init__(self, path):
        with open(path, "r") as f:
            lines = f.readlines()
        self.lines = []
        for i, l in enumerate(lines):
            self.lines.append(SourceLine(i, l))
        self.warnings = self.get_warnings()

    def get_warnings(self):
        warnings = {}
        for i, line in enumerate(self.lines):
            if line.warning_code:
                start, end = self.get_warning_range(i)
                new_warning = {
                        "start": start,
                        "end": end
                }
                if warnings.get(line.warning_code, None):
                    warnings[line.warning_code].append(new_warning)
                else:
                    warnings[line.warning_code] = [new_warning]
        return warnings

    def get_warning_range(self, index):
        regex_start = re.compile(r"/\*")
        regex_end = re.compile(r"\*/")
        start, end = -1, -1
        for i in range(index, -1, -1):
            if regex_start.search(self.lines[i].line):
                start = i
        for i in range(index+1, len(self.lines)):
            if regex_end.search(self.lines[i].line):
                end = i
        if start < 0 or end < 0:
            logging.error("Failed to find DPCT warning range")
            sys.exit(1)
        return start, end
