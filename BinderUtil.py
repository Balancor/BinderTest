#!/usr/bin/env python
#coding:utf-8
import array
import struct
import ctypes
import fcntl, os, time
from Parcel import Parcel
import binascii

BINDER_PATH="/dev/binder"
BINDER_CURRENT_PROTOCOL_VERSION=8
DEFAULT_MAX_BINDER_THREADS = 15

BINDER_TRASACTION_DATA_FORMAT_STRING = 'QQIIIIQQQQ'
FLAT_BINDER_OBJECT_FORMAT_STRING = 'IIQQ'
BINDER_WRITE_READ_FORMAT_STRING = 'QQQQQQ'


B_TYPE_LARGE = 0x85

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
class BinderIOCTL:
    BINDER_WRITE_READ=3224396289
    BINDER_SET_IDLE_TIMEOUT=1074291203
    BINDER_SET_MAX_THREADS=1074029061
    BINDER_SET_IDLE_PRIORITY=1074029062
    BINDER_SET_CONTEXT_MGR=1074029063
    BINDER_THREAD_EXIT=1074029064
    BINDER_VERSION=3221512713

class BinderTransactionFlags:
    TF_ONE_WAY = 0x01
    TF_ROOT_OBJECT = 0x04
    TF_STATUS_CODE = 0x08
    TF_ACCEPT_FDS = 0x10

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
        self.__mReceived = False

        self.__mDriverFD = open(BINDER_PATH, 'r+')
        fcntl.fcntl(self.__mDriverFD, fcntl.F_SETFD, fcntl.FD_CLOEXEC);
        rv = fcntl.fcntl(self.__mDriverFD, fcntl.F_SETFL, os.O_NDELAY)
        buf = array.array('I', [0])
        fcntl.ioctl(self.__mDriverFD, BinderIOCTL.BINDER_VERSION, buf)
        version = struct.unpack('I', buf)[0]
        if version is None or version != BINDER_CURRENT_PROTOCOL_VERSION:
            print "Cannot Open Binder, or Version wrong"
            return

        fcntl.ioctl(self.__mDriverFD, BinderIOCTL.BINDER_SET_MAX_THREADS, struct.pack('I', DEFAULT_MAX_BINDER_THREADS))

    def openDriver(self):
        pass

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
        self.__mOut.submitWrite()

    def talkWithDriver(self, doReceive = True):
        self.__mDriverFD = open(BINDER_PATH, 'r+')
        binderWriteRead = []
        binderWriteRead.append(self.__mOut.ipcDataSize())
        binderWriteRead.append(0)
        binderWriteRead.append(self.__mOut.ipcData())

        readCapacity = 256
        self.__mIn.allocMemory(readCapacity)

        binderWriteRead.append(readCapacity)
        binderWriteRead.append(0)
        binderWriteRead.append(self.__mIn.ipcData())
        binderWriteReadStruct = struct.Struct('=' + BINDER_WRITE_READ_FORMAT_STRING)

        buf = ctypes.create_string_buffer(binderWriteReadStruct.size)
        binderWriteReadStruct.pack_into(buf, 0, *tuple(binderWriteRead))
        fcntl.ioctl(self.__mDriverFD, BinderIOCTL.BINDER_WRITE_READ, ctypes.addressof(buf))

        readConsumedStruct = struct.Struct('Q')
        readConsumed = readConsumedStruct.unpack_from(buf, 32)
        print "readConsumed: ", readConsumed[0]
        if int(readConsumed[0]) > 0:
            self.__mReceived = True

    def transact(self, handle, code, data, reply, flags):
        flags += BinderTransactionFlags.TF_ACCEPT_FDS
        self.writeTransactionData(BinderCommandProtocol.BC_TRANSACTION, flags, handle, code, data)
        if flags & BinderTransactionFlags.TF_ONE_WAY != 0:
            self.talkWithDriver(False)

    def registerToBinder(self):
        outParcel = Parcel()
        flatBinderObject = []

        flatBinderObject.append(BinderType.BINDER_TYPE_BINDER)
        flatBinderObject.append(0x7f | FlatBinderFlag.FLAT_BINDER_FLAG_ACCEPTS_FDS)
        flatBinderObject.append(0)
        flatBinderObject.append(0)
        outParcel.write('IIQQ', flatBinderObject)
        outParcel.submitWrite()
        return outParcel


    def enterServerLoop(self):
        print "Server Ready to enter binder loop"

        data = self.registerToBinder()
        self.transact(0, 0, data, 0, BinderTransactionFlags.TF_ONE_WAY)
#        while(True):
        self.__mReceived = False
        self.talkWithDriver()
        if self.__mReceived:
           print "Received CMD: ", self.__mIn.readInt32()

if __name__ == '__main__':
    binder = BinderUtil()
#binder.openDriver()
