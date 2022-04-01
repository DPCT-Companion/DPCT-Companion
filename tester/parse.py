import yaml


def parse(config_path):
    with open(config_path, mode="r", encoding="UTF-8") as config_file:
        config = yaml.load(config_file, Loader=yaml.CLoader)
    if "build" not in config.keys():
        raise Exception("fail: no build")
    if type(config["build"]) is not dict:
        raise Exception("fail: bad build structure")

    if "test" not in config.keys():
        raise Exception("fail: no test")
    if "cases" not in config["test"].keys():
        raise Exception("fail: no test.cases")
    if isinstance(type(config["test"]["cases"]), list):
        raise Exception("fail: test.cases should be a list")
    test_cases = []
    for case_path in config["test"]["cases"]:
        with open(case_path, mode="r", encoding="UTF-8") as case_file:
            case = yaml.load(case_file, Loader=yaml.CLoader)
            test_cases.append(case)
    return config, test_cases
