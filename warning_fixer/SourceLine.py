import re


class SourceLine:
    def __init__(self, index, line):
        # self.index = index
        self.line = line
        self.warning_code = None
        self.warning_no = None
        self.get_warning_code()

    def get_warning_code(self):
        regex = r".*(DPCT\d{4}):(\d+): "
        result = re.search(regex, self.line)
        if result:
            self.warning_code = result.group(1)
            self.warning_no = result.group(2)
