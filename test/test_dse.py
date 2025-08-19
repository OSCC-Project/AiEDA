#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dse.py
@Time    :   2025-08-19
@Author  :   zhanghongda
@Version :   1.0
@Contact :   zhanghongda24@mails.ucas.ac.cn
@Desc    :   test placement for dse   
'''

######################################################################################
# import aieda
from import_aieda import import_aieda
import_aieda()
######################################################################################
import os
os.environ['eda_tool'] = "iEDA"

from aieda.ai.DSE.dse_facade import DSEFacade
from aieda.data.database.enum import DSEMethod

if __name__ == "__main__":  
    factory = DSEFacade() 

    factory.start(optimize=DSEMethod.NNI)