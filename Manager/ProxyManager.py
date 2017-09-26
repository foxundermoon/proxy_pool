# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import random

from Util import EnvUtil
from DB.DbClient import DbClient
from Util.GetConfig import GetConfig
from Util.LogHandler import LogHandler
from ProxyGetter.getFreeProxy import GetFreeProxy
from Util.EnvUtil import raw_proxy_queue, useful_proxy_queue
import json


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.config = GetConfig()
        self.raw_proxy_queue = raw_proxy_queue
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = useful_proxy_queue

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for proxyGetter in self.config.proxy_getter_functions:
            proxy_dic = dict()
            # fetch raw proxy
            for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                if isinstance(proxy, str):
                    self.log.info('{func}: fetch proxy {proxy}'.format(
                        func=proxyGetter, proxy=proxy))
                    proxy_dic[proxy.strip()] = 1
                elif isinstance(proxy, tuple):
                    ipPort, extra = proxy
                    self.log.info("{func}: fetch proxy {ipPort}:{extra}".format(
                        func=proxyGetter,
                        ipPort=ipPort,
                        extra=json.dumps(extra)
                    ))
                    proxy_dic[ipPort] = extra

            # store raw proxy
            for proxy in proxy_dic:
                if self.db.existsUsed(proxy):
                    continue
                self.db.putRaw(proxy, extra)

    def get(self):
        """
        return a useful proxy
        :return:
        """
        item_dict = self.db.getAllUsed()
        if item_dict:
            key = random.choice(item_dict.keys())
            extra = self.db.getRaw(key)
            return {key: extra}
        return None
        # return self.db.pop()

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        item_dict = self.db.getAllUsed()
        rst = dict()
        for k in item_dict:
            rst[k] = self.db.getRaw(k)
        return rst

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}

if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
    all = pp.getAll()
    print(all)
    total = pp.getNumber()
    print(total)
