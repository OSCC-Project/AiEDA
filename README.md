# AI-EDA Library with iEDA Integration

## User Guide:
- download iEDA and tools
    - $AiEDA_fork: git submodule update --init --recursive
- revise CMakeLists.txt
    - set (PYTHON_EXECUTABLE "/home/huangzengrong/.conda/envs/pda/bin/python") into your local PHTHON_EXECUTABLE 
- compile iEDA
    - $AiEDA_fork: mkdir build
    - $AiEDA_fork: cd build
    - $AiEDA_fork/build: cmake ..
    - $AiEDA_fork/build: make -j32 ieda_py
    
- test "aieda"
    - running iEDA flow
        - $AiEDA_fork: python test/test_ieda_backend.py 
    - analysis design_level data
        - $AiEDA_fork: python test/test_analysis_design.py 