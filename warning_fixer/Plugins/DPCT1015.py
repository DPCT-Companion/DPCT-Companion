import re

from warning_fixer.Plugins.BaseFixer import BaseFixer
from warning_fixer.SourceLine import SourceLine


class DPCT1015(BaseFixer):
    # pattern for format specifiers in format string
    # see https://www.cplusplus.com/reference/cstdio/printf/ for details
    format_specifier_regex = "%[-+#0 ]?(?:\d+|\*)?(?:.\d+|.\*)?(?:hh|h|l|ll|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
    format_specifier_pattern = re.compile(format_specifier_regex)
    str_literal_regex = "\"([^\\\"]|\\.)*\""
    str_literal_pattern = re.compile(str_literal_regex)
    id_regex = "[_a-zA-Z][\w]*"

    arg_regex = f"({str_literal_regex}|{id_regex})"
    arg_pattern = re.compile(arg_regex)
    arg_list_aux_regex = f"[\s\n\t]*,[\s\n\t]*{arg_regex}"
    arg_list_regex = f"{arg_regex}({arg_list_aux_regex})*"
    printf_regex = f"[\s\n\t]*printf[\s\n\t]*\([\s\n\t]*({arg_list_regex})[\s\n\t]*\);"

    def __init__(self, source_lines, cuda_code_line):
        super().__init__(source_lines)
        self.cuda_code_line = cuda_code_line

    def fix(self, start, end):
        temp_lines = self.source_lines
        line, i = self.find_warning_statement(start, end)
        new_code = self._fix(self.cuda_code_line)
        del temp_lines[end + 1: i + 1]
        del temp_lines[start:end + 1]
        temp_lines.insert(start, SourceLine(start, new_code))
        self.source_lines = temp_lines

    def _fix(self, line):
        args = [group[0] for group in DPCT1015.arg_pattern.findall(line)]
        return self.stream_style(args[1].strip('"'), *args[2:])

    def stream_style(self, format_string : str, *args):
        """generate c++ stream style given format string and parameters

        Args:
            format_string (str): first parameter, the format string,  of the printf statement
            args ([]) : list of parameters of the printf statements

        Returns:
            str: the c++ stream style 
        """
        ret = "stream_ct1"
        format_split = DPCT1015.format_specifier_pattern.split(format_string)
        format_match = DPCT1015.format_specifier_pattern.findall(format_string)
        i = 0
        while True:
            if i >= len(format_match): break
            if format_match[i][0] == "%%":
                del format_match[i]
                format_split[i] = format_split[i] + '%' + format_split[i+1]
                del format_split[i+1]
            i += 1
        for i, match in enumerate(format_match):
            if len(format_split[i]) > 0: ret += " << \"" + format_split[i] + "\""
            ret += " << " + args[i]
        if len(format_split[-1]) > 0: ret += " << \"" + format_split[-1] + "\"" + ';'
        return ret

# if __name__ == "__main__":
#     # the printf statement occurs in racon
#     print(repr(DPCT1015.fix("printf(\"assert: lhs=%d, rhs=%d\n\", x, y);")))
#     print(repr(DPCT1015.fix("""printf("assert: lhs=%+13.33jd, rhs=%-*.*hhd\n", x, y);""")))