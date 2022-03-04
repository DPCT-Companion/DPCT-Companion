import re
from pathlib import Path

from warning_fixer.SourceFile import SourceFile


class SourceProject:
    dpct_ext = ["*.dp.cpp", "*.dp.hpp"]
    warning_log_regex = r"(.*):(\d+):\d+: warning: (DPCT\d+:\d+): .*"

    def __init__(self, dpcpp_root_path, cuda_root_path, output_path, log_path):
        self.dpcpp_root_path = dpcpp_root_path
        self.cuda_root_path = cuda_root_path
        self.all_dpct_files = []
        for ext in self.dpct_ext:
            self.all_dpct_files += list(Path(self.dpcpp_root_path).rglob(ext))
        self.output_path = output_path

        with open(log_path, "r") as f:
            self.log_lines = f.readlines()
        self.cuda_file_warning_map = {}
        warning_log_pattern = re.compile(self.warning_log_regex)
        for l in self.log_lines:
            result = warning_log_pattern.search(l)
            if result:
                cuda_file_path = result.group(1)
                if cuda_file_path not in self.cuda_file_warning_map:
                    self.cuda_file_warning_map[cuda_file_path] = {}
                self.cuda_file_warning_map[cuda_file_path][result.group(3)] = int(result.group(2))

    def fix_project_warnings(self):
        for file in self.all_dpct_files:
            cuda_path = str(Path(self.cuda_root_path).joinpath(file.relative_to(self.dpcpp_root_path)))
            if cuda_path[-6:] == "dp.hpp":
                cuda_path = cuda_path[:-6] + "cuh"
            elif cuda_path[-6:] == "dp.cpp":
                cuda_path = cuda_path[:-6] + "cu"
            if str(cuda_path) in self.cuda_file_warning_map:
                fixer = SourceFile(str(file), cuda_path, self.cuda_file_warning_map[cuda_path])
            else:
                if "cudapoa_nw_banded" in cuda_path:
                    print("here")
                fixer = SourceFile(str(file), "", {})
            fixer.fix_warnings()
            new_file_content = "".join([l.line for l in fixer.lines])
            new_path = Path(self.output_path).joinpath(file.relative_to(self.dpcpp_root_path))
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True)
            with open(new_path, "w") as f:
                f.write(new_file_content)


if __name__ == "__main__":
    project = SourceProject(dpcpp_root_path="/Users/tczhang/Desktop/0102/racon2/build/dpcpp",
                            cuda_root_path="/Users/tczhang/Desktop/0102/racon2",
                            output_path="/Users/tczhang/Desktop/0102/racon2/migrated",
                            log_path="/Users/tczhang/Desktop/0102/racon2/build/racon_dpct_local.log")
    project.fix_project_warnings()
