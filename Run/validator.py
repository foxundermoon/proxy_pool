# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     validator.py  
   Description :  运行主函数
   Author :       fox
   date：          2017/9/27
-------------------------------------------------
   Change Activity:
                   2017/9/27: 
-------------------------------------------------
"""
__author__ = 'Fox'

import sys
from multiprocessing import Process
sys.path.append('../')
sys.path.append('./')
from Schedule.ProxyValidSchedule import run

if __name__ == '__main__':
    run()
