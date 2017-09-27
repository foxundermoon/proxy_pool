# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    DbClient.py
   Description :  DB工厂类
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys

from Util.GetConfig import GetConfig
from Util.utilClass import Singleton
from Util.EnvUtil import raw_proxy_queue, useful_proxy_queue, proxy_counter_queue
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(object):
    """
    DbClient DB工厂类 提供get/put/pop/delete/getAll/changeTable方法

    目前存放代理的table/collection/hash有两种：
        raw_proxy： 存放原始的代理；
        useful_proxy_queue： 存放检验后的代理；

    抽象方法定义：
        get(proxy): 返回proxy的信息；
        put(proxy): 存入一个代理；
        pop(): 弹出一个代理
        exists(proxy)： 判断代理是否存在
        getNumber(raw_proxy): 返回代理总数（一个计数器）；
        update(proxy, num): 修改代理属性计数器的值;
        delete(proxy): 删除指定代理；
        getAll(): 返回所有代理；
        changeTable(name): 切换 table or collection or hash;


        所有方法需要相应类去具体实现：
            SSDB：SsdbClient.py
            REDIS:RedisClient.py

    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        init
        :return:
        """
        self.config = GetConfig()
        self.__initDbClient()

    def __initDbClient(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == self.config.db_type:
            __type = "SsdbClient"
        elif "REDIS" == self.config.db_type:
            __type = "RedisClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(
            self.config.db_type)
        self.client = getattr(__import__(__type), __type)(name=self.config.db_name,
                                                          host=self.config.db_host,
                                                          port=self.config.db_port,
                                                          password=self.config.db_password)

    def get(self, key, **kwargs):
        return self.client.get(key, **kwargs)

    def put(self, key, value=1, **kwargs):
        return self.client.put(key, value, **kwargs)

    def update(self, key, value, **kwargs):
        return self.client.update(key, value, **kwargs)

    def updateUsed(self, key, value, **kwargs):
        self.changeUsed()
        return self.update(key, value, **kwargs)

    def updateRaw(self, key, value, **kwargs):
        self.changeRaw()
        return self.update(key, value, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def deleteRaw(self, key, **kwargs):
        self.changeRaw()
        return self.delete(key, **kwargs)

    def deleteUsed(self, key, **kwargs):
        self.changeUsed()
        return self.delete(key, **kwargs)

    def deleteAll(self, key, **kwargs):
        rawRst = self.deleteRaw(key, **kwargs)
        usedRst = self.deleteUsed(key, **kwargs)
        self.changeCounter()
        counterRst = self.delete(key, **kwargs)
        return (rawRst, usedRst, counterRst)

    def exists(self, key, **kwargs):
        return self.client.exists(key, **kwargs)

    def existsUsed(self, key, **kwargs):
        self.changeUsed()
        return self.exists(key, **kwargs)

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)

    def popRaw(self, **kwargs):
        self.changeRaw()
        return self.pop(**kwargs)

    def getAll(self):
        return self.client.getAll()

    def getAllUsed(self):
        self.changeUsed()
        return self.getAll()

    def getAllRaw(self):
        self.changeRaw()
        return self.getAll()

    def increace(self, key, value=1, **kwargs):
        self.changeCounter()
        return self.update(key, value, **kwargs)

    def quality(self, key, **kwargs):
        self.changeCounter()
        return self.get(key, **kwargs)

    def changeTable(self, name):
        self.client.changeTable(name)

    def changeRaw(self):
        self.changeTable(raw_proxy_queue)

    def changeUsed(self):
        self.changeTable(useful_proxy_queue)

    def changeCounter(self):
        self.changeTable(proxy_counter_queue)

    def getRaw(self, key, **kwargs):
        self.changeRaw()
        return self.get(key, **kwargs)

    def getUsed(self, key, **kwargs):
        self.changeUsed()
        return self.get(key, **kwargs)

    def putRaw(self, key, value=1, **kwargs):
        self.changeRaw()
        return self.put(key, value, **kwargs)

    def putUsed(self, key, value=1, **kwargs):
        self.changeUsed()
        return self.put(key, value, **kwargs)

    def getNumber(self):
        return self.client.getNumber()


if __name__ == "__main__":
    db = DbClient()
    proxy1 = "1.2.3.4:88"
    proxy2 = "1.2.3.5:99"
    extra = {'city': "济南", 'isp': "联通"}
    print(db.putRaw(proxy1, extra))
    print(db.putUsed(proxy2))
    print(db.putRaw(proxy2, extra))

    rst = db.getRaw(proxy1)
    print(rst)
    rstU = db.getUsed(proxy2)
    print(rstU)
