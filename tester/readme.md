# Overview

The test harness is developed to perform differential testing on code and migrated code by building and reading the outputs of the processes of the built programs. Specifically, the stdout and stderr are read and compared to generate a report. Also, to enable testing interactive programs, test cases can be specified to write to the stdin and read from the stdout in sequence. 

To use the test harness, both sets of code, their Makefiles and the test cases need to be provided. Executables are built with the build scripts, which are tested with the provided test cases and a test report in the form of a html file to show the results.

# Installation

Retrieve the source code:

```
git clone git@github.com:tianchen-zhang/DPCT-Companion.git
```

Install dependencies:

```
cd DPCT-Companion/tester
pip install -r requirements.txt
```

Use:
```
python main.py tester <args>
```
run the above command in the root directory

A yaml configuration file is utilized to specify details of all provided artifacts. The listing below shows an example of configuration file. 
```
build: 
  cuda-script: make a/Makefile 
  cuda-exec: a/run 
  dpcpp-script: make b/Makefile 
  dpcpp-exec: b/run 
test: 
  cases: [test1.yml, test2.yml] 
  report: report.html 
clean: 
  script: rm a/run && rm b/run 
```
The **cuda-script** and **dpcpp-script** under **build** specify the shell commands to build the source code for cuda and dpcpp respectively (we used Makefiles here) and **cuda-exec** and **dpcpp-exec** specify the path to the executables. 

The **report** under **test** specifies the path and name for the generated report. Test cases are specified by a set of yaml files and paths to which are listed in **cases**, which will be discussed later. 

The **script** under **clean** specify the commands to clean up. 

# Test cases

Yaml file specifying a test case can be separated into two parts, the first part **args** specifies the arguments supplied for running the executables, the second part **steps** lists the sequence of actions required to test the executables.

```
args:
    - arg1
    - arg2
steps:
    - <action1>
    - <action2>
```

Actions available including reading from stdout and stderr, writing to stdin and sleep for specified period. The sequence is specified by a list under the **steps** section. The key can take one of the followings: **check-stdout**, **check-stderr**, **input-stdin** and **sleep**. The action can be further specified by key/value pairs in an optional dictionary object. 

## input-stdin

```
- input-stdin: 
    key: hello! 
    omit-newline: False 
```

**input-stdin** writes to the stdin of the process, where the content is specified by the required field **key**. Additionally, the optional field **omit-newline** specifies whether to omit newline while writing and is False by default. 

## check-stdout

```
- check-stdout: 
    name: check_stdout1 
    omit-line: [3,4,5] 
```
**check-stdout** reads from the stdout of the process and compares the read contents from two executables. The optional **name** field specifies the name of the check and will appear in the final test report. The optional **omit-line** field lists all the lines to be omitted during comparison. A typical use case for the **omit-line** is to ignore lines that include date or time. 

## check-stderr
```
- check-stderr:
    name: check_stderr1
    omit-line: [1,2,3]
```
**check-stderr** is same as **check-stdout** except that it reads and checks stderr instead of stdout. The two fields are the same as those of **check-stdout**.

## sleep
```
- sleep: 2
```
**sleep** requires the tester to sleep for a specified time period (in seconds). A typical use case is to wait for the time-consuming operation of tested programs to complete before checking and comparing stdout. 

## example
The following listing is an example of a test case specification file:
```
args:
    - "-n"
    - 100
steps:
    - sleep: 2 
    - check-stdout: 
        name: stdout1 
        omit-line: [1] 
    - input-stdin: 
        key: hello! 
        omit-newline: False 
    - sleep: 2 
    - check-stdout:  
        name: stdout2 
        omit-line: [1] 
    - check-stderr: 
        name: stderr1 
        omit-line: [2]
```
