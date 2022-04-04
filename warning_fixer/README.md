# Warning Fixer

## Overview
The warning fixer can automatically fix warnings thrown by DPCT.
It can fix the following warnings:
DPCT1003, DPCT1015, DPCT1023 and DPCT1065

## DPCT1003
CUDA uses error codes to detect errors at runtime. 
A non-zero error code indicates an error execution. 
However, DPC++ uses a try- catch style instead of error codes.
DPCT1003 is triggered when an error-checking function takes 
the return value (error code) of another function as input. 
DPC++ would change that return value to 0, and the 
error-checking function would thus be meaningless.

The auto-fixer for DPCT1003 would first use a regular 
expression to find the error-checking function call. 
It simply removes that function call, and the warning 
would be resolved. 
This approach is safe since any errors inside the 
function call would trigger exceptions that, 
if unhandled, would terminate the whole program. 
Such behaviour is also identical to the behaviour of the 
original CUDA code.

For example, the ported DPC++ code looks like
```c++
GW_CU_CHECK_ERR((ptr = (void *)sycl::malloc_device(n * sizeof(T), dpct::get_default_queue()), 0));
```

The warning fixer would fix it to 
```c++
ptr = (void *)sycl::malloc_device(n * sizeof(T), dpct::get_default_queue());
```

## DPCT1015
DPCT1015 is triggered by calling `printf` in kernel 
code since CUDA and DPC++ use different APIs for 
outputting on the device. CUDA uses C-style `printf`, 
whereas DPC++ uses C++-style stream. 
Additionally, as stated by the SYCL documentation, 
`sycl::stream` needs to be used instead of std streams. 
DPCT by default modifies the signature of the kernel function 
by adding an argument named `stream_ct1` of the 
`const sycl::stream&` type, declares the `sycl::stream` object 
and passes it to the kernel function. 
However, it does not fully convert the `printf` statement to an 
equivalent DPC++ stream statement and only outputs the format string.

DPCT Companion fixes the problem by parsing the CUDA printf 
statement and the format string. It recognizes all the specifiers by 
matching regular expressions and replaces them with the arguments.
However, this approach cannot handle cases where format strings 
are provided as variables instead of literal.

For example, CUDA source code like

```cuda
printf("assert: lhs=%d, rhs=%d\n", x, y);
```

would be translated to 
```c++
stream_ct1 << "assert: lhs=" << x << ", rhs=" << y << "\n";
```

## DPCT1023

In CUDA and DPC++, for threads in the same “batch” (“warp” in CUDA and “subgroup” in DPC++), 
there could be a way more efficient way of communicating by directly getting data for a variable 
from other threads without passing through memory. Such functions are called sub-warp functions 
in CUDA and sub-group functions in DPC++. 
They are mostly convertible to one another since their feature set is largely identical. 
But one difference is that the CUDA sub-warp functions support specifying 
masks while the subgroup functions do not, and the “mask” is simply the position of threads 
inside a “batch” that you want to participate in this operation. The DPCT1023 is the warning 
code for this issue.

To resolve DPCT1023, the warning fixer read the CUDA source code and adds an `if` statement to 
guard the subgroup function based on whether the current thread is in the mask. If in the mask 
then the statement is executed, otherwise do nothing.

## DPCT1065

DPCT1065 is triggered by the method sycl::nd_item::barrier(). DPCT would suggest adding an additional 
argument to that method when there are no memory accesses in the global memory to improve the performance. 
The warning fixer automatically detects such method calls in the DPC++ code and adds that argument to these calls.

For example, the ported DPC++ code looks like
```c++
item_ct1.barrier()
```

The warning fixer would fix it to 
```c++
item_ct1.barrier(sycl::access::fence_space::local_space);
```