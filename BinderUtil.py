#!/usr/bin/env python
#coding:utf-8
import array
import struct
import ctypes
import fcntl, os
from Parcel import Parcel

BINDER_PATH="/dev/binder"
BINDER_TRASACTION_DATA_FORMAT_STRING = 'QQIIIIQQQQ'
FLAT_BINDER_OBJECT_FORMAT_STRING = 'IIQQ'
BINDER_WRITE_READ_FORMAT_STRING = 'QQQQQQ'
B_TYPE_LARGE = 0x85

BINDER_WRITE_READ=3224396289
BINDER_SET_IDLE_TIMEOUT=1074291203
BINDER_SET_MAX_THREADS=1074029061
BINDER_SET_IDLE_PRIORITY=1074029062
BINDER_SET_CONTEXT_MGR=1074029063
BINDER_THREAD_EXIT=1074029064
BINDER_VERSION=3221512713

def B_PACK_CHARS_SHORT(c1, c2, c3):
    return (ord(c1) << 24) | \
           (ord(c2) << 16) | \
           (ord(c3) << 8)  | \
           (B_TYPE_LARGE)

def B_PACK_CHARS(c1, c2, c3, c4):
    return (ord(c1) << 24) | \
           (ord(c2) << 16) | \
           (ord(c3) << 8)  | \
           (ord(c4))

class BinderTransaction:
    FIRST_CALL_TRANSACTION  = 0x00000001,
    LAST_CALL_TRANSACTION   = 0x00ffffff,

    PING_TRANSACTION        = B_PACK_CHARS('_','P','N','G')
    DUMP_TRANSACTION        = B_PACK_CHARS('_','D','M','P')
    INTERFACE_TRANSACTION   = B_PACK_CHARS('_', 'N', 'T', 'F')
    SYSPROPS_TRANSACTION    = B_PACK_CHARS('_', 'S', 'P', 'R')


class BinderType:
    BINDER_TYPE_BINDER  = B_PACK_CHARS_SHORT('s', 'b', '*')
    BINDER_TYPE_WEAK_BINDER = B_PACK_CHARS_SHORT('w', 'b', '*')
    BINDER_TYPE_HANDLE  = B_PACK_CHARS_SHORT('s', 'h', '*')
    BINDER_TYPE_WEAK_HANDLE = B_PACK_CHARS_SHORT('w', 'h', '*')
    BINDER_TYPE_FD      = B_PACK_CHARS_SHORT('f', 'd', '*')

class FlatBinderFlag:
    FLAT_BINDER_FLAG_PRIORITY_MASK = 0xff
    FLAT_BINDER_FLAG_ACCEPTS_FDS = 0x100

class BinderCommandProtocol:
    BC_TRANSACTION                   = 1077961472
    BC_REPLY                         = 1077961473
    BC_ACQUIRE_RESULT                = 1074029314
    BC_FREE_BUFFER                   = 1074291459
    BC_INCREFS                       = 1074029316
    BC_ACQUIRE                       = 1074029317
    BC_RELEASE                       = 1074029318
    BC_DECREFS                       = 1074029319
    BC_INCREFS_DONE                  = 1074815752
    BC_ACQUIRE_DONE                  = 1074815753
    BC_ATTEMPT_ACQUIRE               = 1074291466
    BC_REGISTER_LOOPER               = 25355
    BC_ENTER_LOOPER                  = 25356
    BC_EXIT_LOOPER                   = 25357
    BC_REQUEST_DEATH_NOTIFICATION    = 1074553614
    BC_CLEAR_DEATH_NOTIFICATION      = 1074553615
    BC_DEAD_BINDER_DONE              = 1074291472

class BinderReturnProtocol:
    BR_ERROR = 2147774976
    BR_OK = 29185
    BR_TRANSACTION = 2151707138
    BR_REPLY = 2151707139
    BR_ACQUIRE_RESULT = 2147774980
    BR_DEAD_REPLY = 29189
    BR_TRANSACTION_COMPLETE = 29190
    BR_INCREFS = 2148561415
    BR_ACQUIRE = 2148561416
    BR_RELEASE = 2148561417
    BR_DECREFS = 2148561418
    BR_ATTEMPT_ACQUIRE = 2149085707
    BR_NOOP = 29196
    BR_SPAWN_LOOPER = 29197
    BR_FINISHED = 29198
    BR_DEAD_BINDER = 2148037135
    BR_CLEAR_DEATH_NOTIFICATION_DONE = 2148037136
    BR_FAILED_REPLY = 29201

class BinderUtil:
    def __init__(self):
        self.__mOut = Parcel()
        self.__mIn  = Parcel()
        self.__mDriverFD = -1

    def openDriver(self):
        try:
            self.__mDriverFD = open(BINDER_PATH, 'r+')
        except IOError as e:
            if e.errno == errno.EACCES:
                return "some default data"
            # Not a permission error.
            raise
        else:
            with self.__mDriverFD:
                fcntl.fcntl(self.__mDriverFD, fcntl.F_SETFD, fcntl.FD_CLOEXEC);
                rv = fcntl.fcntl(self.__mDriverFD, fcntl.F_SETFL, os.O_NDELAY)
                buf = array.array('I', [0])
                fcntl.ioctl(self.__mDriverFD, BINDER_VERSION, buf)
                print "Binder Version: ",struct.unpack('I', buf)[0]


    def writeTransactionData(self,cmd, binderFlags, handle, code, data):
        transactionValues=[]

        transactionValues.append(handle)
        transactionValues.append(code)
        transactionValues.append(binderFlags)
        transactionValues.append(0)
        transactionValues.append(0)
        transactionValues.append(0)
        transactionValues.append(data.ipcDataSize())
        transactionValues.append(data.ipcData())
        transactionValues.append(0)
        transactionValues.append(0)

        self.__mOut.writeInt32(cmd)
        self.__mOut.write(BINDER_TRASACTION_DATA_FORMAT_STRING, transactionValues)


if __name__ == '__main__':
    binder = BinderUtil()
    binder.openDriver()
