from os import system
from sys import argv
system(f"cd data && dpct {''.join(argv[1:])}")

import yaml
with open("data/dpct_output/MainSourceFiles.yaml", mode="r", encoding="UTF-8") as msf:
    yaml.load(msf, Loader=yaml.CLoader)
