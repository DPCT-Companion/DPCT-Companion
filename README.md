# DPCT-Companion

## Prerequisites

[Python 3](https://www.python.org/downloads/)

[Docker](https://docs.docker.com/get-docker/)

[Docker SDK for Python](https://pypi.org/project/docker/)

## Build & Run

```
python run.py <project_path> [<arg0>... <argN>] <src0>... <srcN>
```

The script will build automatically if the Docker image does not exist. This may take about 20 minutes.

## Build Manually

```
docker build -t patcher patcher
```