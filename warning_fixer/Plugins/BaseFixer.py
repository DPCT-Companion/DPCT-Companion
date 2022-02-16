class BaseFixer:
    def __init__(self, source_lines):
        self.source_lines = source_lines

    def find_warning_statement(self, start, end):
        original_lines = self.source_lines

        initial = True
        temp_code = ""
        for i in range(end + 1, len(original_lines)):
            if ";" not in original_lines[i].line:
                if initial:
                    temp_code += original_lines[i].line
                else:
                    temp_code += original_lines[i].line.strip()
                initial = False
            else:
                if initial:
                    temp_code += original_lines[i].line
                else:
                    temp_code += original_lines[i].line.strip()
                temp_code = temp_code.replace("\n", "")
                return temp_code, i
