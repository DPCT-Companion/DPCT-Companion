import difflib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class Checker:
    """contains results for a single check 'stdin-check' / 'stderr-check'
    """

    def __init__(self, o1, o2, omit_line=None, name=None, c1=None, c2=None):
        self.omit_line = omit_line if omit_line else []
        self.pass_check = True  # does the check pass ?
        self.o1 = o1  # output of cuda
        self.o2 = o2  # output of dpcpp
        self.name = name
        self.c1 = c1  # the return code,
        self.c2 = c2  # see https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.asyncio.subprocess.Process.returncode
        self.check()

    def check(self):
        lines1 = self.o1.split('\n')
        lines2 = self.o2.split('\n')
        self.pass_check = True
        for i, (l1, l2) in enumerate(zip(lines1, lines2)):
            if (i + 1) in self.omit_line:
                continue
            if l1 != l2:
                self.pass_check = False
                break
        if len(lines1) != len(lines2):
            self.pass_check = False


def get_omit_lines_and_names(steps: list):
    omit_lines = []
    names = []
    for step in steps:
        if 'check-stdout' in step:
            v = step['check-stdout']
            omit_line = []
            name = None
            if v is not None and 'omit-line' in v:
                omit_line = v['omit-line']
            if v is not None and 'name' in v:
                name = v['name']
            names.append(name)
            omit_lines.append(omit_line)
        elif 'check-stderr' in step:
            v = step['check-stderr']
            omit_line = []
            name = None
            if v is not None and 'omit-line' in v:
                omit_line = v['omit-line']
            if v is not None and 'name' in v:
                name = v['name']
            names.append(name)
            omit_lines.append(omit_line)
    return omit_lines, names


def check_all(test_cases, cuda_result, dpcpp_result):
    check_results = []
    for case, c_result, d_result in zip(test_cases, cuda_result, dpcpp_result):
        steps = case["steps"]
        cuda_out, cuda_code = c_result
        dpcpp_out, dpcpp_code = d_result
        omit_lines, names = get_omit_lines_and_names(steps)
        check_results.append([Checker(o1, o2, omit_line=omit_line, name=name, c1=c1, c2=c2) for o1, o2, omit_line, name, c1, c2 in
            zip(cuda_out, dpcpp_out, omit_lines, names, cuda_code, dpcpp_code)])
    return check_results


def report(result):
    template = Environment(loader=FileSystemLoader(Path(__file__).resolve().parent), autoescape=True).get_template("report_template.html")
    case_stats = []
    for case in result:
        for check in case:
            check.o1 = [i+'\n' for i in check.o1.splitlines()]
            check.o2 = [i+'\n' for i in check.o2.splitlines()]
        case_stat = {
            "total": len(case),
            "pass": sum(check.pass_check and (check.c1 == 0 or check.c1 is None) and (check.c2 == 0 or check.c2 is None) for check in case),
            "crashed": sum((check.c1 != 0 and check.c1 is not None) or (check.c2 != 0 and check.c2 is not None) for check in case),
            "umatch": len(case) - sum(check.pass_check and (check.c1 == 0 or check.c1 is None) and (check.c2 == 0 or check.c2 is None) for check in case) -
            sum((check.c1 != 0 and check.c1 is not None) or (check.c2 != 0 and check.c2 is not None) for check in case),
            "name": case[0].name,
            "checks": case}
        case_stats.append(case_stat)
    stat = {
        "total": sum(case["total"] for case in case_stats),
        "pass": sum(case["pass"] for case in case_stats),
        "crashed": sum(case["crashed"] for case in case_stats),
        "umatch": sum(case["umatch"] for case in case_stats)}

    with open('report.html', 'w' ) as f:
        r = template.render(stat=stat, case_stats=case_stats, difflib=difflib, list=list)
        f.write(r)
    return r
