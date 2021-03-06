import re
from pathlib import Path

from warning_fixer.SourceFile import SourceFile


class SourceProject:
    dpct_ext = [".hpp", ".h", ".hxx", ".dp.cpp"]
    warning_log_regex = r"(.*):(\d+):\d+: warning: (DPCT\d+:\d+): .*"

    def __init__(self, dpcpp_root_path, cuda_root_path, output_path, log_path):
        self.dpcpp_root_path = Path(dpcpp_root_path).resolve()
        if cuda_root_path is None:
            self.cuda_root_path = None
        else:
            self.cuda_root_path = Path(cuda_root_path).resolve()
        if log_path is None:
            self.log_path = None
        else:
            self.log_path = Path(log_path).resolve()
        # capture all files under dpcpp_root_path
        self.all_dpct_files = filter(
            lambda path: path.is_file() and not any([part for part in path.parts if part.startswith(".")]),
            self.dpcpp_root_path.rglob("*"))
        self.output_path = Path(output_path).resolve()

        if self.log_path is not None:
            with open(self.log_path, "r") as f:
                self.log_lines = f.readlines()
        else:
            self.log_lines = []
        # the map to link warning instances with cuda files
        # each warning instance has a unique index, e.g., 63 in DPCT1015:63: Output needs adjustment.
        # the log of DPCT also includes this index, so we can locate the related cuda file using the log
        # key: cuda file path
        # value: {
        #    key: DPCT warning category and index, e.g., "DPCT1015:63"
        #    value: cuda line no. (which triggers the warning)
        # }
        self.cuda_file_warning_map = {}
        warning_log_pattern = re.compile(self.warning_log_regex)
        for l in self.log_lines:
            result = warning_log_pattern.search(l)
            if result:
                cuda_file_path = Path(result.group(1))
                if cuda_file_path.is_absolute():
                    cuda_file_path = str(cuda_file_path)
                else:
                    cuda_file_path = str(self.log_path.parent.joinpath(cuda_file_path).resolve())
                if cuda_file_path not in self.cuda_file_warning_map:
                    self.cuda_file_warning_map[cuda_file_path] = {}
                self.cuda_file_warning_map[cuda_file_path][result.group(3)] = int(result.group(2))

    def fix_project_warnings(self):
        for file in self.all_dpct_files:
            is_cuda_file = False
            for ext in self.dpct_ext:
                if str(file).endswith(ext):
                    is_cuda_file = True
                    break
            if not is_cuda_file:
                # if not cuda file, keep the file unchanged
                with open(file, "r") as f:
                    new_file_content = f.read()
            else:
                if self.cuda_root_path is None:
                    fixer = SourceFile(str(file), "", {})
                else:
                    cuda_path = str(self.cuda_root_path.joinpath(file.relative_to(self.dpcpp_root_path)))
                    # DPCT naming convention
                    if cuda_path.endswith(".dp.hpp"):
                        cuda_path = cuda_path[:-6] + "cuh"
                    elif (cuda_path.endswith(".cpp.dp.cpp") or
                          cuda_path.endswith(".cc.dp.cpp") or
                          cuda_path.endswith(".cxx.dp.cpp") or
                          cuda_path.endswith(".C.dp.cpp")):
                        cuda_path = cuda_path[:-7]
                    elif cuda_path.endswith(".dp.cpp"):
                        cuda_path = cuda_path[:-6] + "cu"
                    # if we can link the dpcpp file with cuda files, we run the fixer with cuda files
                    # if not, we can still fix the warnings, but the categories which we can fix are limited
                    if str(cuda_path) in self.cuda_file_warning_map:
                        fixer = SourceFile(str(file), cuda_path, self.cuda_file_warning_map[cuda_path])
                    else:
                        fixer = SourceFile(str(file), "", {})
                fixer.fix_warnings()
                new_file_content = "".join([l.line for l in fixer.lines])
            new_path = self.output_path.joinpath(file.relative_to(self.dpcpp_root_path))
            # keep the original directory structure
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True)
            with open(new_path, "w") as f:
                f.write(new_file_content)
