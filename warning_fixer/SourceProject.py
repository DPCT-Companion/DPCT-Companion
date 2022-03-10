import argparse
import re
from pathlib import Path

from warning_fixer.SourceFile import SourceFile


class SourceProject:
    dpct_ext = [".hpp", ".h", ".hxx", ".dp.cpp"]
    warning_log_regex = r"(.*):(\d+):\d+: warning: (DPCT\d+:\d+): .*"

    def __init__(self, dpcpp_root_path, cuda_root_path, output_path, log_path):
        self.dpcpp_root_path = dpcpp_root_path
        self.cuda_root_path = cuda_root_path
        self.all_dpct_files = filter(
            lambda path: path.is_file() and not any([part for part in path.resolve().parts if part.startswith(".")]),
            Path(self.dpcpp_root_path).rglob("*"))
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
            is_cuda_file = False
            for ext in self.dpct_ext:
                if str(file).endswith(ext):
                    is_cuda_file = True
                    break
            cuda_path = str(Path(self.cuda_root_path).joinpath(file.relative_to(self.dpcpp_root_path)))
            if not is_cuda_file:
                with open(file, "r") as f:
                    new_file_content = f.read()
            else:
                if cuda_path.endswith(".dp.hpp"):
                    cuda_path = cuda_path[:-6] + "cuh"
                elif (cuda_path.endswith(".cpp.dp.cpp") or
                      cuda_path.endswith(".cc.dp.cpp") or
                      cuda_path.endswith(".cxx.dp.cpp") or
                      cuda_path.endswith(".C.dp.cpp")):
                    cuda_path = cuda_path[:-7]
                elif cuda_path.endswith(".dp.cpp"):
                    cuda_path = cuda_path[:-6] + "cu"
                if str(cuda_path) in self.cuda_file_warning_map:
                    fixer = SourceFile(str(file), cuda_path, self.cuda_file_warning_map[cuda_path])
                else:
                    fixer = SourceFile(str(file), "", {})
                fixer.fix_warnings()
                new_file_content = "".join([l.line for l in fixer.lines])
            new_path = Path(self.output_path).joinpath(file.relative_to(self.dpcpp_root_path))
            if not new_path.parent.exists():
                new_path.parent.mkdir(parents=True)
            with open(new_path, "w") as f:
                f.write(new_file_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warning fixer of DPCT-Companion")
    parser.add_argument("--dpcpp-root-path", type=str, help="Path of dpct out-root")
    parser.add_argument("--cuda-root-path", type=str, help="Path of dpct in-root")
    parser.add_argument("--output-path", type=str, help="Output path for the fixed code")
    parser.add_argument("--log-path", type=str, help="Path of dpct log")
    args = parser.parse_args()

    if args.dpcpp_root_path and args.cuda_root_path and args.output_path and args.log_path:

        project = SourceProject(dpcpp_root_path=args.dpcpp_root_path,
                                cuda_root_path=args.cuda_root_path,
                                output_path=args.output_path,
                                log_path=args.log_path)
        project.fix_project_warnings()
    else:
        parser.print_usage()
