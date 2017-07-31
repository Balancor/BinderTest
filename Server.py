#!/usr/bin/env python
#coding:utf-8
from BinderUtil import BinderUtil
import os

if __name__ == '__main__':
    print "Server, PID: ", os.getpid()
    binder = BinderUtil()
    binder.enterServerLoop()
