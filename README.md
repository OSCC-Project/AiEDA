# AI-EDA Library with iEDA Integration

## User Guide:
- if run_flow:
    - download iEDA and tools
        - $AiEDA_fork: git submodule update --init --recursive
    - compile iEDA
        - $AiEDA_fork: mkdir build
        - $AiEDA_fork: cd build
        - $AiEDA_fork/build: cmake ..
        - $AiEDA_fork/build: make -j32 ieda_py
    - add \_\_init\_\_.py in third_party/iEDA/bin/.

- package "aieda" library
    - $AiEDA_fork: python setup.py bdist_wheel sdist

- install "aieda" library
    - $AiEDA_fork: pip install dist/aieda-0.1.dev0-py3-none-any.whl 
    
- test "aieda"
    - running iEDA flow
        - $AiEDA_fork: python test/test_ieda_backend.py 
    - analysis design_level data
        - $AiEDA_fork: python test/test_analysis_design.py 