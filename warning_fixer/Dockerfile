FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update && apt-get install git wget gpg software-properties-common -y && wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
RUN apt-get update && apt-get install intel-basekit -y
ENV PATH="/app:/opt/intel/oneapi/dpcpp-ct/latest/bin:${PATH}"

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin && mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 && wget https://developer.download.nvidia.com/compute/cuda/11.4.4/local_installers/cuda-repo-ubuntu2004-11-4-local_11.4.4-470.82.01-1_amd64.deb && dpkg -i cuda-repo-ubuntu2004-11-4-local_11.4.4-470.82.01-1_amd64.deb && apt-key add /var/cuda-repo-ubuntu2004-11-4-local/7fa2af80.pub && apt-get update && apt-get -y install cuda

COPY . /app/warning_fixer
COPY ./requirements.txt /app
COPY ./run.py /app
WORKDIR /app

RUN apt-get install python3 python3-pip -y
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "-u", "run.py" ]
