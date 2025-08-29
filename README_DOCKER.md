# AIEDA Docker 部署指南

本指南说明如何使用Docker来构建和运行AIEDA项目，包括iEDA工具链和Python绑定。

## 快速开始

### 1. 构建Docker镜像

使用提供的构建脚本：

```bash
./build_docker.sh
```

或者手动构建：

```bash
# 构建基础镜像
docker build -f Dockerfile.base -t aieda:base .

# 构建最终镜像
docker build -f Dockerfile.final -t aieda:latest .
```

### 2. 运行测试

运行sky130_gcd测试：

```bash
docker run --rm -it aieda:latest
```

### 3. 交互式使用

进入容器进行交互式操作：

```bash
docker run --rm -it aieda:latest /bin/bash
```

在容器内可以运行：

```bash
# 运行特定测试
python3 test/test_sky130_gcd.py

# 运行其他测试
python3 test/test_ieda_flows.py

# 导入aieda库
python3 -c "import aieda; print('AIEDA imported successfully')"
```

## 文件说明

- `Dockerfile.base`: 基础镜像，包含所有系统依赖和Python环境
- `Dockerfile.final`: 最终镜像，构建iEDA和Python绑定
- `requirements.txt`: Python依赖列表
- `build_docker.sh`: 自动化构建脚本

## 构建过程说明

1. **基础镜像 (Dockerfile.base)**:
   - 安装Ubuntu 22.04基础系统
   - 安装C++编译器、CMake、构建工具
   - 安装iEDA构建所需的系统库
   - 安装Python环境和uv包管理器
   - 安装Python依赖

2. **最终镜像 (Dockerfile.final)**:
   - 基于基础镜像
   - 构建iEDA工具链和Python绑定
   - 安装aieda Python包
   - 设置运行环境

## 自定义配置

### 修改构建参数

可以通过构建参数自定义配置：

```bash
# 指定并行构建线程数
docker build -f Dockerfile.final --build-arg NPROC=8 -t aieda:latest .

# 使用不同的基础镜像
docker build -f Dockerfile.final --build-arg BASE_IMG=my-custom-base -t aieda:latest .
```

### 挂载本地目录

如果需要访问本地文件：

```bash
docker run --rm -it -v /path/to/local/designs:/workspace aieda:latest
```
