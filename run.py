from os import path
from sys import argv

import docker

IMG_NAME = "patcher"

try:
    assert len(argv) > 2
    projectPath = argv[1]
    args = argv[2:]
except:
    print("usage: python run.py <project_path> [<arg0>... <argN>] <src0>... <srcN>")
    exit()

client = docker.from_env()
try:
    client.images.get(IMG_NAME)
except docker.errors.ImageNotFound:
    print("Building the image. This may take about more than 30 minutes.")
    srcPath = path.dirname(path.realpath(__file__))
    client.images.build(path=path.join(srcPath, "patcher"), tag=IMG_NAME)
    print("Build success.")

client.containers.run(IMG_NAME, command=args, volumes={path.abspath(projectPath): {"bind": "/app/data", "mode": "rw"}},
                      remove=True)
