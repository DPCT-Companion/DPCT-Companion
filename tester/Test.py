import asyncio
import os


class Check:
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
            if (i + 1) in self.omit_line: continue
            if l1 != l2:
                self.pass_check = False
                break
        if len(lines1) != len(lines2): self.pass_check = False


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


async def get_tests(case: dict, cuda_exec: str, dpcpp_exec: str):
    args = case["args"]
    steps = case["steps"]
    cuda_out, cuda_code = await get_outputs(args=args, steps=steps, exec=cuda_exec)
    dpcpp_out, dpcpp_code = await get_outputs(args=args, steps=steps, exec=dpcpp_exec)
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
    checks = [Check(o1, o2, omit_line=omit_line, name=name, c1=c1, c2=c2) for o1, o2, omit_line, name, c1, c2 in
              zip(cuda_out, dpcpp_out, omit_lines, names, cuda_code, dpcpp_code)]
    return checks


async def get_all_tests(test_cases: list, cuda_exec: str, dpcpp_exec: str):
    results = []
    for case in test_cases:
        results.append(await get_tests(case, cuda_exec, dpcpp_exec))
    return results


def test(test_cases: list, cuda_exec: str, dpcpp_exec: str) -> any:
    """generate test results

    Args:
        test_cases (list): list of loaded objects from yaml test files
        cuda_exec (str): path of cuda executable
        dpcpp_exec (str): path of dpcpp executable

    Returns:
        [[Check]]: results of each test for each yaml test file
    """
    loop = asyncio.get_event_loop()
    cuda_exec_abs_path = os.path.abspath(cuda_exec)
    dpcpp_exec_abs_path = os.path.abspath(dpcpp_exec)
    task = loop.create_task(get_all_tests(test_cases, cuda_exec_abs_path, dpcpp_exec_abs_path))
    results = loop.run_until_complete(task)
    return results
