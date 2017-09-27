# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyValidSchedule.py
   Description :  验证useful_proxy_queue中的代理,将不可用的移出
   Author :       JHao
   date：          2017/3/31
-------------------------------------------------
   Change Activity:
                   2017/3/31: 验证useful_proxy_queue中的代理
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from time import sleep

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler
import json


class ProxyValidSchedule(ProxyManager):

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('valid_schedule')

    def __validProxy(self):
        """
        验证代理
        :return:
        """
        while True:
            allProxy = self.db.getAllRaw()
            for each_proxy in allProxy:
                value = self.db.getUsed(each_proxy)
                extra = allProxy[each_proxy]
                try:
                    if isinstance(extra, str) and len(extra) > 5:
                        extra = json.loads(extra)
                except Exception:
                    pass
                val = validUsefulProxy((each_proxy, extra))
                if val:
                    # 成功计数器加1
                    if value and int(value) < 1:
                        self.db.updateUsed(each_proxy, 1)
                    self.log.info(
                        'ProxyValidSchedule: {} validation pass'.format(each_proxy))
                    if isinstance(val, dict):
                        self.db.updateRaw(each_proxy, extra)
                else:
                    # 失败计数器减一
                    if value and int(value) < -5:
                        # 计数器小于-5删除该代理
                        self.db.deleteAll(each_proxy)
                    else:
                        self.db.updateUsed(each_proxy, -1)
                        self.log.info(
                            'ProxyValidSchedule: {} validation fail'.format(each_proxy))

            self.log.info('ProxyValidSchedule running normal')
            sleep(60 * 1)

    def main(self):
        self.__validProxy()


def run():
    p = ProxyValidSchedule()
    p.main()


if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
