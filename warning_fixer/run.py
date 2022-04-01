from os import system
from sys import argv

from warning_fixer.SourceProject import *

system(f"cd data && mkdir final_output && dpct {' '.join(argv[1:])}")

project = SourceProject(dpcpp_root_path="/app/data/dpct_output",
                        cuda_root_path="/app/data",
                        output_path="/app/data/final_output",
                        log_path="/app/data/dpct_output/log.log")
project.fix_project_warnings()
