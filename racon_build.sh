git clone https://github.com/lbcb-sci/racon.git
mkdir racon/build && cd racon/build
cmake -DCMAKE_BUILD_TYPE=Release -Dracon_enable_cuda=ON -Dracon_build_test=ON ..
sed -i '3475 s/operator""_format/operator_format/' _deps/genomeworks-src/3rdparty/spdlog/include/spdlog/fmt/bundled/format.h
source /opt/intel/oneapi/setvars.sh
intercept-build make
sed -i '46 s/min(t1, min(t2, t3))/t1<(t2<t3?t2:t3)?t1:(t2<t3?t2:t3)/' _deps/genomeworks-src/common/base/include/claraparabricks/genomeworks/utils/mathutils.hpp

# run DPCT or DPCT-Companion
# dpct -p=. --in-root=.. --out-root=./dpcpp --extra-arg="-D__CUDA_ARCH__=750" --extra-arg="-I/usr/lib/llvm-10/include/openmp" --extra-arg="-DTHRUST_IGNORE_CUB_VERSION_CHECK=1" &> racon_dpct.log
