# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Baina Info Inc. All rights reserved.
@Author : Zuowei Zhang
@Date : 2012-08-09
'''


class MyAppRouter(object):

    def db_for_read(self, model, **hints):
        return self.__app_router(model)

    def db_for_write(self, model, **hints):
        return self.__app_router(model)

#    def allow_relation(self, obj1, obj2, **hints):
#        return obj1._state.db == obj2._state.db

    def allow_syncdb(self, db, model):
        return self.__app_router(model) == db

    def __app_router(self, model):
        DolphinService_en = ('DolphinService_en',)
        DolphinService_zh = ('DolphinService_zh',)
        if model._meta.app_label in DolphinService_en:
            return 'sonar_en'
        elif model._meta.app_label in DolphinService_zh:
            return 'sonar_zh'
        return 'default'
