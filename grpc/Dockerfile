FROM ubuntu:22.04

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    autoconf \
    libtool \
    pkg-config \
    cmake \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# gRPCとProtobufをソースからビルド
WORKDIR /opt
RUN git clone --recurse-submodules -b v1.62.0 https://github.com/grpc/grpc.git
WORKDIR /opt/grpc
RUN mkdir -p build && cd build && \
    cmake .. \
    -DgRPC_INSTALL=ON \
    -DgRPC_BUILD_TESTS=OFF \
    -DgRPC_BUILD_CSHARP_EXT=OFF \
    && make -j$(nproc) && make install

WORKDIR /opt
RUN git clone https://github.com/yuanyuanJ/gRPC-pertest.git
WORKDIR /opt/gRPC-pertest
RUN mkdir -p build && cd build && \
    cmake .. \
    && make
CMD ["/usr/bin/sleep", "infinity"]

