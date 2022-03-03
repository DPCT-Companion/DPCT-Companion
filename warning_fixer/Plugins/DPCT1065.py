import re

from warning_fixer.Plugins.BaseFixer import BaseFixer


class DPCT1065(BaseFixer):

   
    def __init__(self, source_lines, start, end):
        super().__init__(source_lines, start, end)
        self.fixing_code = "DPCT1065"
    
    def fix(self):
        temp_code, statement_start, statement_end, consecutive_warnings = self.find_warning_statement()

        new_code = temp_code
        regex = r"(\s*\S+)(\.barrier)(\()(\))"
        result = re.search(regex, temp_code)
        if result:
            new_code = result.group(1) + result.group(2) + result.group(3)+"sycl::access::fence_space::local_space"+result.group(4) + ";\n"
        self.replace_code(new_code, statement_start, statement_end, consecutive_warnings)


    
   



   

   
       

      

