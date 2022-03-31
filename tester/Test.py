import asyncio
import os
import pickle

from tester.Build import build
from tester.Checker import check_all, report


async def get_outputs(args: list, steps: list, exec: str):
    out1 = []
    code = []
    proc = await asyncio.subprocess.create_subprocess_exec(
        exec,
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    for step in steps:
        if 'check-stdout' in step:
            out1.append((await proc.stdout.read(1024)).decode())
            code.append(proc.returncode)
        elif 'check-stderr' in step:
            out1.append((await proc.stderr.read(1024)).decode())
            code.append(proc.returncode)
        elif 'input-stdin' in step:
            v = step['input-stdin']
            key = str(v['key'])
            if not 'omit-newline' in v or not v['omit-newline']: key += '\n'
            proc.stdin.write(key.encode())
        elif 'sleep' in step:
            sleep_time = step['sleep']
            await asyncio.sleep(sleep_time)
    await proc.wait()
    return out1, code


async def get_tests(case: dict, exec: str):
    args = case["args"]
    steps = case["steps"]
    out, code = await get_outputs(args=args, steps=steps, exec=exec)
    return out, code


async def get_all_tests(test_cases: list, exec: str) -> list:
    results = []
    for case in test_cases:
        results.append(await get_tests(case, exec))
    return results


def do_test(test_cases: list, cuda_exec: str, dpcpp_exec: str, platform: str) -> any:
    """generate test results

    Args:
        test_cases (list): list of loaded objects from yaml test files
        cuda_exec (str): path of cuda executable
        dpcpp_exec (str): path of dpcpp executable
        mode (str): mode of the tests, could be partial or full
        platform (str): platform on which the tests would run, could be cuda, dpcpp or cuda,dpcpp

    Returns:
        cuda_result: list of CUDA tests running results, None if not specified
        dpcpp_result: list of DPC++ tests running results, None if not specified
    """
    loop = asyncio.get_event_loop()
    if "cuda" in platform:
        cuda_exec_abs_path = os.path.abspath(cuda_exec)
        cuda_task = loop.create_task(get_all_tests(test_cases, cuda_exec_abs_path))
        cuda_result = loop.run_until_complete(cuda_task)
    else:
        cuda_result = None

    if "dpcpp" in platform:
        dpcpp_exec_abs_path = os.path.abspath(dpcpp_exec)
        dpcpp_task = loop.create_task(get_all_tests(test_cases, dpcpp_exec_abs_path))
        dpcpp_result = loop.run_until_complete(dpcpp_task)
    else:
        dpcpp_result = None

    return cuda_result, dpcpp_result


def run_tester(config, test_cases, platform, check, reports):
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
