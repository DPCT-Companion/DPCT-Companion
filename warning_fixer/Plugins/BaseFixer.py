import re

from warning_fixer.SourceLine import SourceLine


class BaseFixer:
    def __init__(self, source_lines, start, end):
        self.source_lines = source_lines
        self.start = start
        self.end = end
        self.fixing_code = ""

    # find the statement which triggers the warning and its range
    def find_warning_statement(self):
        original_lines = self.source_lines

        # handle consecutive warnings
        # sometimes more than one warnings appear consecutively before one certain statement
        # which means one statement triggers several warnings
        # we need to locate these warnings, and remove the warning message when we fix that warning
        temp_code_lines = []
        consecutive_warning_lines = []
        statement_end = -1
        for i in range(self.end + 1, len(original_lines)):
            if original_lines[i].warning_code:
                consecutive_warning_lines.append(i)
            if ";" not in original_lines[i].line:
                temp_code_lines.append(original_lines[i].line)
            else:
                temp_code_lines.append(original_lines[i].line)
                statement_end = i
                break

        consecutive_warnings = []
        for warning_line in consecutive_warning_lines:
            regex_start = re.compile(r"/\*")
            regex_end = re.compile(r"\*/")
            warning_start, warning_end = -1, -1
            for i in range(warning_line, -1, -1):
                if regex_start.search(original_lines[i].line):
                    warning_start = i
                    break
            for i in range(warning_line + 1, len(original_lines)):
                if regex_end.search(original_lines[i].line):
                    warning_end = i
                    break
            if warning_start != -1 and warning_end != -1:
                consecutive_warnings.append((original_lines[warning_line].warning_code, warning_start, warning_end))
        # the start line no of the warning statement is the next line of the last line of the last consecutive warnings
        if consecutive_warnings:
            statement_start = consecutive_warnings[-1][-1] + 1
        else:
            statement_start = self.end + 1
        statement_lines = [l.replace("\n", " ") for l in temp_code_lines[statement_start - self.end - 1:]]
        for i in range(1, len(statement_lines)):
            statement_lines[i] = statement_lines[i].strip()
        statement = "".join(statement_lines)
        # statement is the actual warning statement
        # statement_start and statement_end are the range of that statement in the original file
        # consecutive_warnings is the information about consecutive warnings
        return statement, statement_start, statement_end, consecutive_warnings

    def replace_code(self, new_code, statement_start, statement_end, consecutive_warnings):
        del self.source_lines[statement_start:statement_end + 1]
        inserted = False
        # remove all the instances in the consecutive warnings with the same warning code
        # while keep all the other warning messages
        for code, warning_start, warning_end in consecutive_warnings[::-1]:
            if code == self.fixing_code:
                del self.source_lines[warning_start:warning_end + 1]
            elif not inserted:
                self.insert_new_code(new_code, warning_end + 1)
                inserted = True
        del self.source_lines[self.start:self.end + 1]
        if not inserted:
            self.insert_new_code(new_code, self.start)

    def insert_new_code(self, new_code, index):
        insert_list = new_code.splitlines(True)
        for i, line in enumerate(insert_list):
            self.source_lines.insert(index + i, SourceLine(index + i, line))
