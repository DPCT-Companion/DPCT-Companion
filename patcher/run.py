from os import system
from sys import argv
system(f"cd data && dpct {' '.join(argv[1:])}")

from re import compile
pattern = compile("/*\n *DPCT(\d{4}):\d+: ")

class Warning:
    def __init__(self, code, filePath, fileOffset, oldLength):
        self.code = code
        self.filePath = filePath
        self.offset = fileOffset
        self.oldLength = oldLength

    def __repr__(self):
        return f"<Warning{self.code}@{self.filePath}:{self.offset}>"

warnings = []

import yaml
with open("data/dpct_output/MainSourceFiles.yaml", mode="r", encoding="UTF-8") as msfFile:
    msf = yaml.load(msfFile, Loader=yaml.CLoader)
    replacements = msf["Replacements"]
    for replacement in replacements:
        result = pattern.search(replacement["ReplacementText"])
        if result:
            DPCTCode = result.group(1)
            warnings.append(Warning(DPCTCode, 
                replacement["FilePath"][10:], 
                replacement["Offset"], 
                replacement["Length"]))
print(warnings)
