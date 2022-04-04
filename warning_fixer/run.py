from sys import argv
from subprocess import run

from warning_fixer.SourceProject import *

logPath = "/app/data/dpct_output/log.log"
with open(logPath) as logFile:
    run(f"cd data && mkdir final_output && dpct {' '.join(argv[1:])}", shell=True, stdout=logFile, check=True)

project = SourceProject(dpcpp_root_path="/app/data/dpct_output",
                        cuda_root_path="/app/data",
                        output_path="/app/data/final_output",
                        log_path=logPath)
project.fix_project_warnings()
