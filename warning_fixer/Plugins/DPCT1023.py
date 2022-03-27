"""
    Class which implemented the fixer of DPCT1023 warning.

    Input cuda_code_line: The line of CUDA code which triggered this warning (Get it from the DPCT log)
    Input dpcxx_code_line: The line of valid code immediately following the warning (I would recommend to use ";" for delimiter, since the code can technically span more than one line)

    Output: A string which contains fixed lines of code. None on error.

    LIMITATION: NVIDIA CUDA apps mostly assume a warp size of 32, so masks are mostly indicating 32 lanes as well. For this warning to *POSSIBLY* be fixed, our DPC++ kernel MUST BE launched using 32-thread-wide SIMD subgroups.
    If subgroup size is not 32, even manually fixing it will be a big headache.
"""

import re

from warning_fixer.Plugins.BaseFixer import BaseFixer


class DPCT1023(BaseFixer):
    known_full_mask_name = {"FULL_MASK", "0xffff'ffffu"}
    fix_skeleton = "{} {} {};\nsycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & {})\n{{\n    {}\n}}\n"

    def __init__(self, source_lines, cuda_code_line, start, end):
        super().__init__(source_lines, start, end)
        self.cuda_code_line = cuda_code_line
        self.dpcxx_code_line = ""
        self.fixing_code = "DPCT1023"

    def normalize_input(self):
        self.cuda_code_line = " ".join(self.cuda_code_line.split()).strip()
        self.dpcxx_code_line = " ".join(self.dpcxx_code_line.split()).strip()

    def fix(self):
        temp_code, statement_start, statement_end, consecutive_warnings = self.find_warning_statement()
        self.dpcxx_code_line = temp_code
        self.normalize_input()
        new_code = self.dpcxx_code_line

        # Regex pattern to get the mask variable / constant from the original CUDA line of code.
        mask_var_patt = re.compile(r"[\s\S]*\(\s*(\S+)\s*,\s*(\S+)\s*,[\s\S]*")
        dpcxx_ret_patt = re.compile(r"[\s\S]*?(\S+)\s*([+\-*/]?=)[\s\S]*")
        mask_result = re.search(mask_var_patt, self.cuda_code_line)
        dpcxx_ret_result = re.search(dpcxx_ret_patt, self.dpcxx_code_line)
        if (mask_result is not None) and (dpcxx_ret_result is not None):

            # Mask variable / constant
            mask_var_name = mask_result.group(1)

            # Shuffle target variable
            source_var_name = mask_result.group(2)

            # DPC++ sub-group return variable and operator
            ret_var_name = dpcxx_ret_result.group(1)
            ret_var_operator = dpcxx_ret_result.group(2)

            # Full mask, no fix necessary.
            if mask_var_name in self.known_full_mask_name:
                new_code = temp_code + "\n"

            # Not full mask (or does not recognize that it is full mask), insert conditional statement.
            else:
                new_code = self.fix_skeleton.format(ret_var_name, ret_var_operator, source_var_name, mask_var_name,
                                                    self.dpcxx_code_line)

        self.replace_code(new_code, statement_start, statement_end, consecutive_warnings)
