'''
    Class which implemented the fixer of DPCT1023 warning.

    Input cuda_code_line: The line of CUDA code which triggered this warning (Get it from the DPCT log)
    Input dpcxx_code_line: The line of valid code immediately following the warning (I would recommend to use ";" for delimiter, since the code can technically span more than one line)
    
    Output: A string which contains fixed lines of code. None on error.
    
    LIMITATION: NVIDIA CUDA apps mostly assume a warp size of 32, so masks are mostly indicating 32 lanes as well. For this warning to *POSSIBLY* be fixed, our DPC++ kernel MUST BE launched using 32-thread-wide SIMD subgroups.
    If subgroup size is not 32, even manually fixing it will be a big headache.
'''

import re

from warning_fixer.Plugins.BaseFixer import BaseFixer
from warning_fixer.SourceLine import SourceLine


class DPCT1023(BaseFixer):

    known_full_mask_name = set(["FULL_MASK", "0xffff'ffffu"])
    fix_skeleton = "{} = {};\nsycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & {})\n{{\n    {}\n}}\n"

    def __init__(self, source_lines, cuda_code_line):
        super().__init__(source_lines)
        self.cuda_code_line = cuda_code_line
        self.dpcxx_code_line = ""

    def normalize_input(self):
        self.cuda_code_line = " ".join(self.cuda_code_line.split()).strip()
        self.dpcxx_code_line = " ".join(self.dpcxx_code_line.split()).strip()

    def fix(self, start, end):
        temp_lines = self.source_lines
        temp_code, i = self.find_warning_statement(start, end)
        self.dpcxx_code_line = temp_code
        self.normalize_input()
        new_code = self.dpcxx_code_line

        # Regex pattern to get the mask variable / constant from the original CUDA line of code.
        mask_var_patt = re.compile(r".*\( ?(\S+) ?, ?(\S+) ?.*")
        dpcxx_ret_patt = re.compile(r"(\S+) ?= ?.*")
        mask_result = re.search(mask_var_patt, self.cuda_code_line)
        dpcxx_ret_result = re.search(dpcxx_ret_patt, self.dpcxx_code_line)
        if mask_result:

            # Mask variable / constant
            mask_var_name = mask_result.group(1)

            # Shuffle target variable
            source_var_name = mask_result.group(2)

            # DPC++ sub-group return variable
            ret_var_name = dpcxx_ret_result.group(1)

            # Full mask, no fix necessary.
            if mask_var_name in self.known_full_mask_name:
                new_code = self.dpcxx_code_line

            # Not full mask (or does not recognize that it is full mask), insert conditional statement.
            else:
                new_code = self.fix_skeleton.format(ret_var_name, source_var_name, mask_var_name, self.dpcxx_code_line)

        del temp_lines[end + 1: i + 1]
        del temp_lines[start:end + 1]
        temp_lines.insert(start, SourceLine(start, new_code))
        self.source_lines = temp_lines
