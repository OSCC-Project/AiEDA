cmake_minimum_required(VERSION 3.16)
project(aieda)

set(CMAKE_CXX_STANDARD 20)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})

set(BUILD_AIEDA "ON")
add_subdirectory(${PROJECT_SOURCE_DIR}/aieda/third_party/iEDA)