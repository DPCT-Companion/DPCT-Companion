FROM ubuntu:18.04

RUN apt-get update && apt-get install wget gpg -y && wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
RUN apt-get update && apt-get install intel-basekit -y
ENV PATH="/opt/intel/oneapi/dpcpp-ct/latest/bin:${PATH}"
RUN apt-get install nvidia-cuda-toolkit -y

COPY . /app
WORKDIR /app

RUN apt-get install python3 python3-pip -y
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "run.py" ]