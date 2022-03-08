import os
import asyncio

class Check:
    """contains results for a single check 'stdin-check' / 'stderr-check'
    """
    def __init__(self, o1, o2, omit_line=None, name=None):
        self.omit_line = omit_line if omit_line else []
        self.pass_check = True  # does the check pass ?
        self.o1 = o1            # output of cuda
        self.o2 = o2            # output of dpcpp
        self.name = name
        self.check()
    def check(self):
        lines1 = self.o1.split('\n')
        lines2 = self.o2.split('\n')
        self.pass_check = True
        for i, (l1, l2) in enumerate(zip(lines1, lines2)):
            if (i+1) in self.omit_line: continue
            if l1 != l2:
                self.pass_check = False
                break
        if len(lines1) != len(lines2): self.pass_check = False

async def get_outputs(steps : list, exec: str):
    out1 = []
    proc = await asyncio.subprocess.create_subprocess_exec(
        exec, 
        stdin=asyncio.subprocess.PIPE, 
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE
    )
    for step in steps:
        if 'check-stdout' in step:
            v = step['check-stdout']
            out1.append((await proc.stdout.read(1024)).decode())
        elif 'check-stderr' in step:
            v = step['check-stderr']
            out1.append((await proc.stderr.read(1024)).decode())
        elif 'input-stdin' in step:
            v = step['input-stdin']
            key = v['key']
            if not 'omit-newline' in v or not v['omit-newline']: key += '\n'
            proc.stdin.write(key.encode())
        elif 'sleep' in step:
            sleep_time = step['sleep']
            await asyncio.sleep(sleep_time)
    await proc.wait()
    return out1

async def get_tests(steps : list, cuda_exec : str, dpcpp_exec : str):
    cuda_out = await get_outputs(steps, exec=cuda_exec)
    dpcpp_out = await get_outputs(steps, exec=dpcpp_exec)
    omit_lines = []
    names = []
    for step in steps:
        if 'check-stdout' in step:
            v = step['check-stdout']
            omit_line = []
            name = None
            if v != None and 'omit-line' in v:
                omit_line = v['omit-line']
            if v != None and 'name' in v:
                name = v['name']
            names.append(name)
            omit_lines.append(omit_line)
        elif 'check-stderr' in step:
            v = step['check-stderr']
            omit_line = []
            name = None
            if v != None and 'omit-line' in v:
                omit_line = v['omit-line']
            if v != None and 'name' in v:
                name = v['name']
            names.append(name)
            omit_lines.append(omit_line)
    checks = [Check(o1, o2, omit_line=omit_line, name=name) for o1, o2, omit_line, name in zip(cuda_out, dpcpp_out, omit_lines, names)]
    return checks

async def get_all_tests(test_cases : list, cuda_exec : str, dpcpp_exec : str):
    results = []
    for steps in test_cases:
        results.append(await get_tests(steps, cuda_exec, dpcpp_exec))
    return results

def test(test_cases: list, cuda_exec : str, dpcpp_exec: str) -> any:
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
    dpcpp_exec_abs_path= os.path.abspath(dpcpp_exec)
    task = loop.create_task(get_all_tests(test_cases, cuda_exec_abs_path, dpcpp_exec_abs_path))
    results = loop.run_until_complete(task)
    return results