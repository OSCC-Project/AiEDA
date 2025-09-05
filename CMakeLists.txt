cmake_minimum_required(VERSION 3.16)
project(aieda)

set(CMAKE_CXX_STANDARD 20)

set(BUILD_AIEDA "ON")
add_subdirectory(${PROJECT_SOURCE_DIR}/aieda/third_party/iEDA)