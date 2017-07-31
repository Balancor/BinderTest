#!/usr/bin/env python
#coding:utf-8
import time
import os
import mmap
from BinderUtil import BinderUtil

BINDER_PATH="/dev/binder"
MAP_SIZE=128*1024


if __name__ == '__main__':
    binder = BinderUtil()
    fd = open(BINDER_PATH, 'r+')
    mm = mmap.mmap(fileno = fd.fileno(), length = MAP_SIZE, flags = mmap.MAP_PRIVATE, prot = mmap.PROT_READ)
    binder.becomBinderManager()
    while True:
        time.sleep(5)
        print "I am BinderManager, and is running, PID: ", os.getpid()
    mm.close
    f.close()
