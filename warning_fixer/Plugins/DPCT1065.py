import re

from warning_fixer.Plugins.BaseFixer import BaseFixer
from warning_fixer.SourceLine import SourceLine


class DPCT1065(BaseFixer):

   
    def __init__(self, source_lines):
        super().__init__(source_lines)

    
    def fix(self, start, end):
        temp_lines = self.source_lines
        
        temp_code, i = self.find_warning_statement(start, end)

        new_code = temp_code
        regex = r"(\S+)(\.barrier)(\()(\))"
        result = re.search(regex, temp_code)
        if result:
            new_code = result.group(1) + result.group(2) + result.group(3)+"sycl::access::fence_space::local_space"+result.group(4)
        del temp_lines[end+1: i+1]
        del temp_lines[start:end+1]
        temp_lines.insert(start, SourceLine(start, new_code))
        self.source_lines = temp_lines


    
   



   

   
       

      

