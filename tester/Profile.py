"""
Tester module to profile the built executable on GPU.
For NVIDIA CUDA, we use NVIDIA Nsight Compute (NCU), and for DPC++ we use Intel VTune profiler.
Before running it, Intel oneAPI environment must be initialized and NVIDIA Nsight Compute (NCU) must be installed.
Profiler is run on SYNC manner with a timeout.

Args:
    cuda_exec (str): The CUDA executable name.
    dpcpp_exec (str): The DPC++ executable name.
    timeout (int): Timeout in seconds to terminate the profiler.

Returns:
    profiler_message (dict: {str, float}):
        "cuda_gpu_time": CUDA GPU active time in microseconds.
        "cuda_gpu_sm_active": NVIDIA GPU SM (Streaming Multiprocessor) active percentage.
        "dpcpp_gpu_time": DPC++ GPU active time in microseconds.
        "dpcpp_gpu_eu_idle": Intel GPU EU (Execution Unit) active percentage.
"""

import re
import subprocess


def profile(cuda_exec: str, dpcpp_exec: str, timeout: int) -> dict:
    try:
        cuda_profile_gpu_cmd = "ncu --target-processes all {}".format(cuda_exec)
        cuda_gpu_time_patt = re.compile(r"Duration usecond (\d+\.\d+)")
        cuda_gpu_sm_active_patt = re.compile(r"Compute \(SM\) \[%] % (\d+\.\d+)")
        print("Profiling Original CUDA program. Timeout is {} seconds.".format(timeout))
        result = subprocess.run(cuda_profile_gpu_cmd.split(), timeout=timeout, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, encoding="utf-8")

        cuda_profiler_output = " ".join(result.stdout.split()).strip()
        cuda_gpu_time_list = re.findall(cuda_gpu_time_patt, cuda_profiler_output)
        cuda_gpu_sm_active_list = re.findall(cuda_gpu_sm_active_patt, cuda_profiler_output)
        cuda_gpu_time = 0.0
        for time in cuda_gpu_time_list:
            cuda_gpu_time += float(time)
        cuda_gpu_sm_active = 0.0
        for time in cuda_gpu_sm_active_list:
            cuda_gpu_sm_active += float(time)
        cuda_gpu_sm_active /= len(cuda_gpu_sm_active_list)

        dpcpp_profile_gpu_cmd = "vtune -collect gpu-hotspots {}".format(dpcpp_exec)
        dpcpp_gpu_time_patt = re.compile(r"GPU Time: (\d+\.\d+)s")
        dpcpp_gpu_eu_efficiency_patt = re.compile(r"EU Array Stalled/Idle: (\d+\.\d+)%")
        print("Profiling ported DPC++ program. Timeout is {} seconds.".format(timeout))
        result = subprocess.run(dpcpp_profile_gpu_cmd.split(), timeout=timeout, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, encoding="utf-8")
        dpcpp_profiler_output = result.stdout
        dpcpp_gpu_time = float(re.search(dpcpp_gpu_time_patt, dpcpp_profiler_output).group(1)) * 1000000.0
        dpcpp_gpu_eu_active = 100.0 - float(re.search(dpcpp_gpu_eu_efficiency_patt, dpcpp_profiler_output).group(1))

        return {"cuda_gpu_time": cuda_gpu_time,
                "cuda_gpu_sm_active": cuda_gpu_sm_active,
                "dpcpp_gpu_time": dpcpp_gpu_time,
                "dpcpp_gpu_eu_active": dpcpp_gpu_eu_active}

    except subprocess.TimeoutExpired as e:
        print("Timed out in profiling. Complete output message for the profiler is printed below for reference:\n")
        print("========stdout========")
        print(e.stdout)
        print("\n========stderr========")
        print(e.stderr)
        return {"cuda_gpu_time": 0.0,
                "cuda_gpu_sm_active": 0.0,
                "dpcpp_gpu_time": 0.0,
                "dpcpp_gpu_eu_active": 0.0}
