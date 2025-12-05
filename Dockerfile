# Global args
ARG BASE_IMAGE=docker.m.daocloud.io/library/ubuntu:22.04
#==============================================================================
# Stage 1: Build environment
#==============================================================================
FROM ${BASE_IMAGE} AS builder

LABEL maintainer="qiuyihang23@mails.ucas.ac.cn"

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive \
    UV_HTTP_TIMEOUT=300 \
    UV_CONCURRENT_DOWNLOADS=1

# System setup and dependencies installation
RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    sed -i -e 's@//archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' \
           -e 's@//security.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends apt-utils ca-certificates && \
    # Python and basic tools
    apt-get install -y --no-install-recommends \
        python3-pip python3.10 python3.10-dev python3.10-venv \
        git wget unzip curl && \
    # Build tools
    apt-get install -y --no-install-recommends \
        build-essential g++-10 cmake ninja-build pkg-config && \
    # Development libraries
    apt-get install -y --no-install-recommends \
        tcl-dev libgflags-dev libgoogle-glog-dev libboost-all-dev \
        libgtest-dev flex libeigen3-dev libunwind-dev libmetis-dev \
        libgmp-dev bison rustc cargo libhwloc-dev libcairo2-dev \
        libcurl4-openssl-dev libtbb-dev && \
    # Runtime libraries (needed for building)
    apt-get install -y --no-install-recommends \
        libcurl4 libunwind8 libgomp1 libtcl8.6 libtk8.6 libcairo2 && \
    # Cleanup
    apt-get autoremove -y && apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    # Install uv
    pip3 install --no-cache-dir -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple uv

ARG AIEDA_WORKSPACE=/opt/aieda
WORKDIR ${AIEDA_WORKSPACE}

COPY . .
RUN uv pip install --system -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple -e .

# Build C++ extension
RUN mkdir -p build && \
    cd build && \
    cmake -S .. -B . \
        -DCMAKE_CXX_COMPILER=g++-10 \
        -DCMAKE_C_COMPILER=gcc-10 \
        -DCMAKE_BUILD_TYPE=Release \
        -GNinja && \
    ninja -j$(nproc) ieda_py && \
    # Cleanup build artifacts but keep the built library
    find . -name "*.o" -delete && \
    find . -name "*.ninja*" -delete

#==============================================================================
# Stage 2: Runtime environment  
#==============================================================================
FROM ${BASE_IMAGE} AS runtime

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# Install only runtime dependencies
RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    sed -i -e 's@//archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' \
           -e 's@//security.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends apt-utils ca-certificates && \
    # Python runtime
    apt-get install -y --no-install-recommends python3 python3-pip && \
    # Runtime libraries (match what was used in builder)
    apt-get install -y --no-install-recommends libcurl4 libunwind8 libgomp1 libtcl8.6 libtk8.6 libcairo2 && \
    apt-get install -y --no-install-recommends libgflags2.2 libgoogle-glog0v5 libtbb12 libhwloc15 && \
    apt-get install -y --no-install-recommends libboost-system1.74.0 libboost-filesystem1.74.0 libboost-thread1.74.0 && \
    apt-get install -y --no-install-recommends libboost-program-options1.74.0 libboost-regex1.74.0 && \
    # X11 and GUI support
    apt-get install -y --no-install-recommends \
        x11-apps \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libdbus-1-3 && \
    # XCB libraries (Qt platform plugin dependencies)
    apt-get install -y --no-install-recommends \
        libxcb-xinerama0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xfixes0 \
        libxcb-shape0 \
        libxcb-shm0 \
        libxcb-sync1 \
        libxcb-xkb1 \
        libxcb-util1 \
        libxkbcommon-x11-0 \
        libxkbcommon0 && \
    # QtWebEngine (Chromium) dependencies
    apt-get install -y --no-install-recommends \
        libnss3 \
        libnspr4 \
        libasound2 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxtst6 \
        libxcursor1 \
        libxi6 \
        libxss1 \
        libpci3 \
        libxshmfence1 \
        libxkbfile1 \
        libdrm2 \
        libgbm1 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libcups2 \
        libpango-1.0-0 && \
    # Cleanup
    apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ARG AIEDA_WORKSPACE=/opt/aieda
ENV PYTHONPATH="${AIEDA_WORKSPACE}"
ENV PATH="${AIEDA_WORKSPACE}/aieda/third_party/iEDA/bin:$PATH"
# Set Qt environment variables for better X11 compatibility
ENV QT_X11_NO_MITSHM=1

WORKDIR ${AIEDA_WORKSPACE}

# Copy everything from builder
COPY --from=builder ${AIEDA_WORKSPACE} ${AIEDA_WORKSPACE}
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages

# Default command
CMD ["/usr/bin/env", "python3", "test/test_sky130_gcd.py"]