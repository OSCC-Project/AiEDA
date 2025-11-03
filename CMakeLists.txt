cmake_minimum_required(VERSION 3.16)
project(aieda)

set(CMAKE_CXX_STANDARD 20)

# Set Python interpreter path to use virtual environment Python
set(PYTHON_EXECUTABLE "${CMAKE_SOURCE_DIR}/.venv/bin/python3")

# Check if virtual environment Python exists
if(EXISTS "${PYTHON_EXECUTABLE}")
    message(STATUS "Using virtual environment Python: ${PYTHON_EXECUTABLE}")
    
    # Get Python version from virtual environment
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" --version
        OUTPUT_VARIABLE PYTHON_VERSION_OUTPUT
        ERROR_VARIABLE PYTHON_VERSION_ERROR
        RESULT_VARIABLE PYTHON_VERSION_RESULT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE
    )
    if(PYTHON_VERSION_RESULT EQUAL 0)
        message(STATUS "Virtual environment Python version: ${PYTHON_VERSION_OUTPUT}")
    else()
        message(STATUS "Virtual environment Python version: ${PYTHON_VERSION_ERROR}")
    endif()
else()
    # Fallback to system python3 if virtual environment doesn't exist
    message(WARNING "Virtual environment Python not found at ${PYTHON_EXECUTABLE}")
    message(WARNING "Falling back to system python3")
    
    execute_process(
        COMMAND python3 --version
        OUTPUT_VARIABLE PYTHON_VERSION_OUTPUT
        ERROR_VARIABLE PYTHON_VERSION_ERROR
        RESULT_VARIABLE PYTHON_VERSION_RESULT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE
    )
    if(PYTHON_VERSION_RESULT EQUAL 0)
        message(STATUS "Using system Python version: ${PYTHON_VERSION_OUTPUT}")
    else()
        message(STATUS "Using system Python version: ${PYTHON_VERSION_ERROR}")
    endif()
    
    execute_process(
        COMMAND which python3
        OUTPUT_VARIABLE PYTHON_EXECUTABLE
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message(STATUS "System Python path: ${PYTHON_EXECUTABLE}")
endif()

# Export PYTHON_EXECUTABLE for use in subdirectories
set(PYTHON_EXECUTABLE "${PYTHON_EXECUTABLE}" CACHE PATH "Python executable path" FORCE)

set(BUILD_AIEDA "ON")
add_subdirectory(${PROJECT_SOURCE_DIR}/aieda/third_party/iEDA)