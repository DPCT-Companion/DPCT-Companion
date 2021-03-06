import subprocess
from typing import Tuple


def build(build_config: dict, platform: str) -> Tuple[str, str]:
    if "cuda" in platform:
        if "cuda-exec" not in build_config:
            raise Exception("fail: no build.cuda-exec")
        if type(build_config["cuda-exec"]) is not str:
            raise Exception("fail: build.cuda-exec should be a string")
        if "cuda-script" in build_config:
            if type(build_config["cuda-script"]) is not str:
                raise Exception("fail: build.cuda-script should be a string")
            # TODO: Fix this naive implementation
            subprocess.run(build_config["cuda-script"].split(" "), check=True)

    if "dpcpp" in platform:
        if "dpcpp-exec" not in build_config:
            raise Exception("fail: no build.dpcpp-exec")
        if type(build_config["dpcpp-exec"]) is not str:
            raise Exception("fail: build.dpcpp-exec should be a string")
        if "dpcpp-script" in build_config:
            if type(build_config["dpcpp-script"]) is not str:
                raise Exception("fail: build.dpcpp-script should be a string")
            # TODO: Fix this naive implementation
            subprocess.run(build_config["dpcpp-script"].split(" "), check=True)

    return build_config.get("cuda-exec", ""), build_config.get("dpcpp-exec", "")
