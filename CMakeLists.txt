cmake_minimum_required(VERSION 3.16)
project(aieda)

set(CMAKE_CXX_STANDARD 20)

# The required Python version should be higher than 3.13.0.
set(PYTHON_EXECUTABLE "your_python_execute_path")

set(BUILD_AIEDA "ON")
add_subdirectory(${PROJECT_SOURCE_DIR}/aieda/third_party/iEDA)