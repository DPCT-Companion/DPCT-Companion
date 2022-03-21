from typing import Dict
from sys import argv
import yaml
from jinja2 import Environment, FileSystemLoader
import difflib

from Build import build
from Test import test
from Profile import profile
from Clean import clean

def report(result):
    template = Environment(loader=FileSystemLoader("."), autoescape=True).get_template("report_template.html")
    for check in result:
        check.o1 = [i+'\n' for i in check.o1.splitlines()]
        check.o2 = [i+'\n' for i in check.o2.splitlines()]
    stat = {
        "total": len(result),
        "pass": sum(check.pass_check for check in result),
        "crashed": sum(check.c1 for check in result),
        "umatch": sum(not check.pass_check for check in result) - sum(check.c1 for check in result)}

    with open('report.html', 'w' ) as f:
        f.write(template.render(checks=result, stat=stat, difflib=difflib, list=list))


if __name__ == '__main__':
    try:
        assert len(argv) == 2
        config_path = argv[1]
    except:
        print("usage: python run.py configPath")
        exit()

    with open(config_path, mode="r", encoding="UTF-8") as config_file:
        config = yaml.load(config_file, Loader=yaml.CLoader)
        if "build" not in config.keys():
            raise Exception("fail: no build")
        if type(config["build"]) is not dict:
            raise Exception("fail: bad build structure")
        cuda_exec, dpcpp_exec = build(config["build"])
        if cuda_exec is None:
            raise Exception("fail: no cuda executable")
        if dpcpp_exec is None:
            raise Exception("fail: no dpcpp executable")
        
        if "test" not in config.keys():
            raise Exception("fail: no test")
        if "cases" not in config["test"].keys():
            raise Exception("fail: no test.cases")
        if type(config["test"]["cases"]) is not list:
            raise Exception("fail: test.cases should be a list")
        test_cases = []
        for case_path in config["test"]["cases"]:
            with open(case_path, mode="r", encoding="UTF-8") as case_file:
                case = yaml.load(case_file, Loader=yaml.CLoader)
                test_cases.append(case)
        # print(test_cases, cuda_exec, dpcpp_exec)
        result = test(test_cases, cuda_exec, dpcpp_exec)
        # TODO : export to report
        report(result)

        # TODO: Place the timeout value in yaml specification.
        # TODO: Export profiler message to report.
        # Profiler is not enabled right now.
        # profiler_message = profile(dpcpp_exec, 300)

        if "clean" in config.keys():
            clean(config["clean"])
