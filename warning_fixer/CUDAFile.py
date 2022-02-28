class CUDAFile:
    def __init__(self, path):
        with open(path, "r") as f:
            self.lines = f.readlines()

    def get_statement_from_line_no(self, line_no):
        initial = True
        temp_code = ""
        for i in range(line_no, len(self.lines)):
            if ";" not in self.lines[i]:
                if initial:
                    temp_code += self.lines[i]
                else:
                    temp_code += self.lines[i].strip()
                initial = False
            else:
                if initial:
                    temp_code += self.lines[i]
                else:
                    temp_code += self.lines[i].strip()
                temp_code = temp_code.replace("\n", "")
                return temp_code
