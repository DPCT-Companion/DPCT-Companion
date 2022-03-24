import re

from warning_fixer.Plugins.BaseFixer import BaseFixer


class DPCT1003(BaseFixer):
    def __init__(self, source_lines, start, end):
        super().__init__(source_lines, start, end)
        self.fixing_code = "DPCT1003"

    def fix(self):
        temp_code, statement_start, statement_end, consecutive_warnings = self.find_warning_statement()
        # remove function call to error-code-handling functions
        new_code = temp_code
        regex = r"[a-zA-Z_][a-zA-Z0-9_]*\(\s*\((.*),\s*0\)\);"
        result = re.search(regex, temp_code)
        if result:
            new_code = temp_code[:result.span(0)[0]] + result.group(1) + ";\n"

        self.replace_code(new_code, statement_start, statement_end, consecutive_warnings)
