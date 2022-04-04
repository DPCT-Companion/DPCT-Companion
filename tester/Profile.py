import re
import subprocess

from tester.Build import build


def profile_cuda(cuda_exec, test_cases, timeout):
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
    cuda_profile_gpu_cmd = "ncu --target-processes all --replay-mode application --app-replay-buffer memory {}"
    cuda_gpu_time_patt = re.compile(r"Duration ([um]?second) (\d+\.\d+)")
    cuda_gpu_sm_active_patt = re.compile(r"Compute \(SM\) \[%] % (\d+\.\d+)")
    print("Profiling Original CUDA program. Timeout is {} seconds.".format(timeout))
    cuda_profile_result = []
    for i, case in enumerate(test_cases):
        args = case["args"]
        if args is None:
            full_command = cuda_exec
        else:
            new_args = []
            for arg in args:
                if arg is None:
                    continue
                try:
                    new_args.append(str(arg))
                except Exception:
                    raise Exception("Illegal argument")
            full_command = " ".join([cuda_exec] + new_args)
        try:
            result = subprocess.run(cuda_profile_gpu_cmd.format(full_command).split(), timeout=timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", check=True)
            cuda_profiler_output = " ".join(result.stdout.split()).strip()
            cuda_gpu_time_list = re.findall(cuda_gpu_time_patt, cuda_profiler_output)
            cuda_gpu_sm_active_list = re.findall(cuda_gpu_sm_active_patt, cuda_profiler_output)
            cuda_gpu_time = 0.0
            for time in cuda_gpu_time_list:
                cur_time = float(time[1])
                if time[0] == "usecond":
                    cur_time /= 1000
                elif time[0] == "second":
                    cur_time *= 1000
                cuda_gpu_time += cur_time
            cuda_gpu_sm_active = 0.0
            for time in cuda_gpu_sm_active_list:
                cuda_gpu_sm_active += float(time)
            cuda_gpu_sm_active /= len(cuda_gpu_sm_active_list)
            cuda_profile_result.append({"cuda_gpu_time": cuda_gpu_time, "cuda_gpu_sm_active": cuda_gpu_sm_active})

        except subprocess.TimeoutExpired as e:
            print("Timed out for test case " + str(i)
                  + ". Complete output message for the profiler is printed below for reference:\n")
            print("========stdout========")
            print(e.stdout)
            print("\n========stderr========")
            print(e.stderr)
            cuda_profile_result.append({"cuda_gpu_time": 0.0, "cuda_gpu_sm_active": 0.0})

        except Exception as e:
            print("Error occurred for test case " + str(i) + ". ")
            cuda_profile_result.append({"cuda_gpu_time": 0.0, "cuda_gpu_sm_active": 0.0})
    return cuda_profile_result


def profile_dpcpp(dpcpp_exec, test_cases, timeout):
    dpcpp_profile_gpu_cmd = "vtune -collect gpu-hotspots {}"
    dpcpp_gpu_time_patt = re.compile(r"GPU Time: (\d+\.\d+)s")
    dpcpp_gpu_eu_efficiency_patt = re.compile(r"EU Array Stalled/Idle: (\d+\.\d+)%")
    print("Profiling ported DPC++ program. Timeout is {} seconds.".format(timeout))
    dpcpp_profile_result = []
    for i, case in enumerate(test_cases):
        args = case["args"]
        if args is None:
            full_command = dpcpp_exec
        else:
            new_args = []
            for arg in args:
                if arg is None:
                    continue
                try:
                    new_args.append(str(arg))
                except Exception:
                    raise Exception("Illegal argument")
            full_command = " ".join([dpcpp_exec] + new_args)
        try:
            result = subprocess.run(dpcpp_profile_gpu_cmd.format(full_command).split(), timeout=timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", check=True)
            dpcpp_profiler_output = result.stdout
            dpcpp_gpu_time = float(re.search(dpcpp_gpu_time_patt, dpcpp_profiler_output).group(1)) * 1000.0
            dpcpp_gpu_eu_active = 100.0 - float(re.search(dpcpp_gpu_eu_efficiency_patt, dpcpp_profiler_output).group(1))
            dpcpp_profile_result.append({"dpcpp_gpu_time": dpcpp_gpu_time, "dpcpp_gpu_eu_active": dpcpp_gpu_eu_active})
        except subprocess.TimeoutExpired as e:
            print("Timed out for test case " + str(i)
                  + ". Complete output message for the profiler is printed below for reference:\n")
            print("========stdout========")
            print(e.stdout)
            print("\n========stderr========")
            print(e.stderr)
            dpcpp_profile_result.append({"dpcpp_gpu_time": 0.0, "dpcpp_gpu_eu_active": 0.0})
        except Exception as e:
            print("Error occurred for test case " + str(i))
            dpcpp_profile_result.append({"dpcpp_gpu_time": 0.0, "dpcpp_gpu_eu_active": 0.0})
    return dpcpp_profile_result


def profile(config, test_cases, platform, timeout):
    cuda_exec, dpcpp_exec = build(config["build"], platform)
    cuda_profile_result = []
    dpcpp_profile_result = []
    if "cuda" in platform:
        cuda_profile_result = profile_cuda(cuda_exec, test_cases, timeout)
    if "dpcpp" in platform:
        dpcpp_profile_result = profile_dpcpp(dpcpp_exec, test_cases, timeout)
    for i in range(len(test_cases)):
        print("Profiler result for test case", i)
        if "cuda" in platform:
            cr = cuda_profile_result[i]
            print("CUDA:\tGPU Time:", "%.2f" % (cr["cuda_gpu_time"]) + "ms\tSM Active:",
                  "%.2f%%" % (cr["cuda_gpu_sm_active"]))
        if "dpcpp" in platform:
            dr = dpcpp_profile_result[i]
            print("DPC++:\tGPU Time:", "%.2f" % (dr["dpcpp_gpu_time"]) + "ms\tEU Active: ",
                  "%.2f%%" % (dr["dpcpp_gpu_eu_active"]))
        print()
