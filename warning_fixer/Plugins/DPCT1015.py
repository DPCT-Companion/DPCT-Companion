import re

class DPCT1015:
    # pattern for format specifiers in format string
    # see https://www.cplusplus.com/reference/cstdio/printf/ for details
    format_specifier_regex = "%[-+#0 ]?[diuoxXfFeEgGaAcspn%]"
    format_specifier_pattern = re.compile(format_specifier_regex)
    str_literal_regex = "\"([^\\\"]|\\.)*\""
    str_literal_pattern = re.compile(str_literal_regex)
    id_regex = "[_a-zA-Z][\w]*"

    arg_regex = f"({str_literal_regex}|{id_regex})"
    arg_pattern = re.compile(arg_regex)
    arg_list_aux_regex = f"[\s\n\t]*,[\s\n\t]*{arg_regex}"
    arg_list_regex = f"{arg_regex}({arg_list_aux_regex})*"
    printf_regex = f"[\s\n\t]*printf[\s\n\t]*\([\s\n\t]*({arg_list_regex})[\s\n\t]*\);"

    def fix(line : str):
        args = [group[0] for group in DPCT1015.arg_pattern.findall(line)]
        return DPCT1015.stream_style(args[1].strip('"'), *args[2:])

    def stream_style(format_string : str, *args):
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
            if format_match[i] == "%%":
                del format_match[i]
                format_split[i] = format_split[i] + '%' + format_split[i+1]
                del format_split[i+1]
            i += 1
        for i, match in enumerate(format_match):
            if len(format_split[i]) > 0: ret += " << \"" + format_split[i] + "\""
            ret += " << " + args[i]
        if len(format_split[-1]) > 0: ret += " << \"" + format_split[-1] + "\"" + ';'
        return ret

if __name__ == "__main__":
    # the printf statement occurs in racon
    print(repr(DPCT1015.fix("printf(\"assert: lhs=%d, rhs=%d\n\", x, y);")))
    print(repr(DPCT1015.stream_style("assert: lhs=%d, rhs=%d\n", "x", "y")))
    print(repr(DPCT1015.arg_list_regex))