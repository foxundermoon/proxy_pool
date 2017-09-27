# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyRefreshSchedule.py
   Description :  代理定时刷新
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4: 代理定时刷新
                   2017/03/06: 使用LogHandler添加日志
                   2017/04/26: raw_proxy_queue验证通过但useful_proxy_queue中已经存在的代理不在放入
-------------------------------------------------
"""

import sys
import time
import logging
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

__author__ = 'JHao'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('refresh_schedule')

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        raw_proxy = self.db.popRaw()
        self.log.info('ProxyRefreshSchedule: %s start validProxy' %
                      time.ctime())
        while raw_proxy:
            extra = validUsefulProxy(raw_proxy)
            if extra:
                self.db.putUsed(raw_proxy, extra)
                self.log.info(
                    "ProxyRefreshSchedule: {} validation pass :{}".format(
                        raw_proxy, extra)
                )
            else:
                self.log.info(
                    'ProxyRefreshSchedule: %s validation fail' % raw_proxy
                    )
            raw_proxy = self.db.popRaw()
        self.log.info(
            'ProxyRefreshSchedule: %s validProxy complete' % time.ctime()
        )


def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def main(process_num=30):
    p = ProxyRefreshSchedule()

    # 获取新代理
    p.refresh()

    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = Thread(target=refreshPool, args=())
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    for num in range(process_num):
        pl[num].join()


def run():
    main()
    sched = BlockingScheduler()
    sched.add_job(main, 'interval', minutes=10)  # 每10分钟抓取一次
    sched.start()


if __name__ == '__main__':
    run()
