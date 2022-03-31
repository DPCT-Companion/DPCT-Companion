import pickle

import yaml

from tester.Build import build
from tester.Checker import check_all, report
from tester.Test import do_test


def run_tester(config_path, platform, check, reports):
    with open(config_path, mode="r", encoding="UTF-8") as config_file:
        config = yaml.load(config_file, Loader=yaml.CLoader)
    if "build" not in config.keys():
        raise Exception("fail: no build")
    if type(config["build"]) is not dict:
        raise Exception("fail: bad build structure")

    if "test" not in config.keys():
        raise Exception("fail: no tests")
    if "cases" not in config["tests"].keys():
        raise Exception("fail: no tests.cases")
    if isinstance(type(config["tests"]["cases"]), list):
        raise Exception("fail: tests.cases should be a list")
    test_cases = []
    for case_path in config["tests"]["cases"]:
        with open(case_path, mode="r", encoding="UTF-8") as case_file:
            case = yaml.load(case_file, Loader=yaml.CLoader)
            test_cases.append(case)

    # no need to build the target when mode is check
    if not check:
        cuda_exec, dpcpp_exec = build(config["build"], platform)
        cuda_result, dpcpp_result = do_test(test_cases, cuda_exec, dpcpp_exec, platform)

        if platform == "cuda":
            with open("cuda_test_result.par", "wb") as f:
                pickle.dump(cuda_result, f)
        if platform == "dpcpp":
            with open("dpcpp_test_result.par", "wb") as f:
                pickle.dump(dpcpp_result, f)

    if check:
        with open(reports[0], "rb") as f:
            cuda_result = pickle.load(f)
        with open(reports[1], "rb") as f:
            dpcpp_result = pickle.load(f)
    if check or platform == "cuda,dpcpp":
        check_results = check_all(test_cases, cuda_result, dpcpp_result)
        report(check_results)

    # TODO: Place the timeout value in yaml specification.
    # TODO: Export profiler message to report.
    # Profiler is not enabled right now.
    # profiler_message = profile(dpcpp_exec, 300)
