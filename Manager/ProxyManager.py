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
            proxy_list = list()
            # fetch raw proxy
            for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                proxy_list.append(proxy)
                if isinstance(proxy, str):
                    self.log.info('{func}: fetch proxy {proxy}'.format(
                        func=proxyGetter, proxy=proxy))
                elif isinstance(proxy, tuple):
                    ipPort, extra = proxy
                    self.log.info("{func}: fetch proxy {ipPort}:{extra}".format(
                        func=proxyGetter,
                        ipPort=ipPort,
                        extra=extra
                    ))

            # store raw proxy
            for proxy in proxy_list:
                ipPort = None
                extra = None
                if isinstance(proxy, str):
                    ipPort = proxy
                if isinstance(proxy, tuple):
                    ipPort, extra = proxy
                if self.db.existsUsed(ipPort):
                    continue
                self.db.putRaw(ipPort, extra)

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
        self.db.deleteAll(proxy)

    def getAll(self, **kwargs):
        """
        get all proxy from pool as list
        :return:
        """
        rst = dict()
        item_dict = self.db.getAllUsed()
        if item_dict:
            for k, v in item_dict.items():
                rst[k] = json.loads(v)
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
