'''
    Class which implemented the fixer of DPCT1023 warning.

    Input cuda_code_line: The line of CUDA code which triggered this warning (Get it from the DPCT log)
    Input dpcxx_code_line: The line of valid code immediately following the warning (I would recommend to use ";" for delimiter, since the code can technically span more than one line)
    
    Output: A string which contains fixed lines of code. None on error.
'''

import re

class DPCT1023:

    known_full_mask_name = set("FULL_MASK", "0xffff'ffffu")
    fix_skeleton = "sycl::ext::oneapi::sub_group sg_DPCTCOM = item_ct1.get_sub_group();\nint sgId_DPCTCOM = sg_DPCTCOM.get_local_id()[0];\nif ((1 << sgId_DPCTCOM) & {})\n{{\n    {}\n}}\n"

    def __init__(self, cuda_code_line: str, dpcxx_code_line: str):
        self.cuda_code_line = cuda_code_line
        self.dpcxx_code_line = dpcxx_code_line

    def normalize_input(self):
        self.cuda_code_line = " ".join(self.cuda_code_line.split()).strip()
        self.dpcxx_code_line = " ".join(self.dpcxx_code_line.split()).strip()

    def fix(self):
        self.normalize_input()

        # Regex pattern to get the mask variable / constant from the original CUDA line of code.
        mask_var_patt = re.compile(r".*\( ?(\S+) ?,.*")
        result = re.search(mask_var_patt, self.cuda_code_line)
        if result:

            # Mask variable / constant
            mask_var_name = result.group(1)

            # Full mask, no fix necessary.
            if mask_var_name in self.known_full_mask_name:
                return self.dpcxx_code_line

            # Not full mask (or does not recognize that it is full mask), insert conditional statement.
            else:
                return self.fix_skeleton.format(mask_var_name, self.dpcxx_code_line)
        else:
            return None
