"""
Tester module to profile the built executable on GPU.
Currently, Nsight profilers cannot be run on our machines, only Intel VTune profiler will work.
Before running it, Intel oneAPI environment must be initialized.
Profiler is run on SYNC manner with a timeout.

Args:
    dpcpp_exec (str): The executable name.
    timeout (int): Timeout in seconds to terminate the profiler.

Returns:
    profiler_message (dict: {str, float}):
        "gpu_time": GPU active time in seconds.
        "gpu_eu_idle": GPU EU (Execution Unit) idle time versus total possible time in percentage. Indicator of GPU uArch efficiency.
"""

import re
import subprocess


def profile(dpcpp_exec: str, timeout: int) -> dict:
    try:
        dpcpp_profile_gpu_cmd = "vtune -collect gpu-hotspots {}".format(dpcpp_exec)
        gpu_time_patt = re.compile(r"GPU Time: (\d+\.\d+)s")
        gpu_eu_efficiency_patt = re.compile(r"EU Array Stalled/Idle: (\d+\.\d+)%")

        print("Profiling ported DPC++ program. Timeout is {} seconds.".format(timeout))
        result = subprocess.run(dpcpp_profile_gpu_cmd.split(), capture_output=True, timeout=timeout,
                                stderr=subprocess.STDOUT, encoding="utf-8")
        profiler_output = result.stdout

        gpu_time = float(re.search(gpu_time_patt, profiler_output).group(1))
        gpu_eu_idle = float(re.search(gpu_eu_efficiency_patt, profiler_output).group(1))

        return {"gpu_time": gpu_time,
                "gpu_eu_idle": gpu_eu_idle}



    except subprocess.TimeoutExpired as e:
        print("Timed out in profiling. Complete output message for the profiler is printed below for reference:\n")
        print("========stdout========")
        print(e.stdout)
        print("\n========stderr========")
        print(e.stderr)
        return {"gpu_time": 0.0,
                "gpu_eu_idle": 0.0}
