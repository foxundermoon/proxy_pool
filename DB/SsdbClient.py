# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     SsdbClient.py
   Description :  封装SSDB操作
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
                   2017/09/22: PY3中 redis-py返回的数据是bytes型
-------------------------------------------------
"""
__author__ = 'JHao'

from Util import EnvUtil

from redis.connection import BlockingConnectionPool
from redis import Redis
import random
import json


class SsdbClient(object):
    """
    SSDB client

    SSDB中代理存放的容器为hash：
        原始代理存放在name为raw_proxy的hash中，key为代理的ip:port，value为为None,以后扩展可能会加入代理属性；
        验证后的代理存放在name为useful_proxy的hash中，key为代理的ip:port，value为一个计数,初始为1，每校验失败一次减1；

    """

    def __init__(self, name, host, port, password=None):
        """
        init
        :param name: hash name
        :param host: ssdb host
        :param port: ssdb port
        :return:
        """
        self.name = name
        self.__conn = Redis(connection_pool=BlockingConnectionPool(
            host=host, port=port, password=password))

    def get(self, proxy):
        """
        get an item
        从hash中获取对应的proxy, 使用前需要调用changeTable()
        :param proxy:
        :return:
        """
        data = self.__conn.hget(name=self.name, key=proxy)
        if isinstance(data, str):
            if len(data) > 4:
                try:
                    return json.loads(data)
                except Exception:
                    pass
            return data
        elif isinstance(data, int):
            return data
        else:
            return None

    def put(self, proxy, value):
        """
        将代理放入hash, 使用changeTable指定hash name
        :param proxy:
        :param num:
        :return:
        """
        if isinstance(value, int):
            data = self.__conn.hincrby(self.name, proxy, value)
        elif isinstance(value, str):
            data = self.__conn.hset(self.name, proxy, value)
        else:
            data = self.__conn.hset(self.name, proxy, json.dumps(value))
        return data

    def delete(self, key):
        """
        Remove the ``key`` from hash ``name``
        :param key:
        :return:
        """
        return self.__conn.hdel(self.name, key)

    def update(self, key, value):
        if isinstance(value, int):
            self.__conn.hincrby(self.name, key, value)
        elif isinstance(value, str):
            self.__conn.hset(self.name, key, value)
        else:
            self.__conn.hset(self.name, key, json.dumps(value))

    def pop(self):
        proxies = self.__conn.hkeys(self.name)
        if proxies:
            proxy = random.choice(proxies)
            extra = self.get(proxy)
            self.delete(proxy)
            return (proxy, extra)
        return None

    def exists(self, key):
        return self.__conn.hexists(self.name, key)

    def getAll(self):
        item_dict = self.__conn.hgetall(self.name)
        return item_dict

    def getNumber(self):
        """
        Return the number of elements in hash ``name``
        :return:
        """
        return self.__conn.hlen(self.name)

    def changeTable(self, name):
        self.name = name
