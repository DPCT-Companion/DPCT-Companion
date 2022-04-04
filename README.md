# DPCT-Companion

## Prerequisites

[Python 3](https://www.python.org/downloads/)

[Intel oneAPI Base Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html)

[CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)

## Running DPCT-Companion

### Warning Fixer

The warning fixer can fix DPCT1003, DPCT1015, DPCT1023, and DPCT1065 thrown by DPCT. To run the warning fixer, execute: 

`python3 main.py fixer [-h] -d DPCPP_ROOT_PATH [-c CUDA_ROOT_PATH] -o OUTPUT_PATH [-l LOG_PATH]`

Specifying cuda_root_path and log_path can enable fixer for DPCT1015 and DPCT1023.

### Test Harness

The test harness can test the CUDA version and DPC++ version of the application.

To run the harness on CUDA platform:

`python3 main.py tester -p cuda <config_file>`

The partial report will be saved in `cuda_test_result.par`.

To run the harness on DPC++ platform:

`python3 main.py tester -p dpcpp <config_file>`

The partial report will be saved in `dpcpp_test_result.par`.

To run the comparison of the two platforms:

`python3 main.py tester -p both <config_file>`

or use two partial reports:

`python3 main.py tester --check <config_file> <partial_report_1> <partial_report_2>`

The output will be saved in an HTML file.

### Profiler

The profiler can profile the CUDA version and DPC++ version of the application. It uses 
[NVIDIA Nsight Computer](https://developer.nvidia.com/nsight-compute) for CUDA environment and
[Intel Vtune Profiler](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html)
for DPC++ environment.

To run the profiler on CUDA platform:

`python3 main.py profiler -p cuda <config_file>`

To run the harness on DPC++ platform:

`python3 main.py profiler -p dpcpp <config_file>`

To run the comparison of the two platforms:

`python3 main.py tester -p both <config_file>`