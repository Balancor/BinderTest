#!/usr/bin/env python
#coding:utf-8
import array, ctypes,fcntl, os, struct, time,
from Parcel import Parcel
from BinderUtil import BinderUtil

if __name__ == '__main__':
    binder = BinderUtil()
    binder.transact()
