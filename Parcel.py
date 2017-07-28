#!/usr/bin/env python
#coding:utf-8
import binascii
import ctypes
import struct
import types


class Parcel:
    def __init__(self):
        self.__mRawData__ = []
        self.__mDataSize__ = 0
        self.__mDataWritePos__ = 0
        self.__mDataReadPos__ = 0
        self.__mDataFormatString__ = "="
        self.__mStringInfo__ = []
        self.__mStringNo__ = 0
        self.__mStringReadNo__ = 0
        self.__mObjectInfo__= []
        self.__mObjectNo__ = 0
        self.__mObjectReadNo__ = 0

    def writeByte(self, value):
        self.__mDataFormatString__ += 'b'
        self.__mRawData__.append(value)
        self.__mDataWritePos__ += 1

    def write2Bytes(self, value):
        self.__mDataFormatString__ += 'h'
        self.__mRawData__.append(value)
        self.__mDataWritePos__ += 2

    def write4Bytes(self, value):
        self.__mDataFormatString__ += 'I'
        self.__mRawData__.append(value)
        self.__mDataWritePos__ += 4

    def write8Bytes(self, value):
        self.__mDataFormatString__ += 'Q'
        self.__mRawData__.append(value)
        self.__mDataWritePos__ += 8

    def writeFloat(self, value):
        self.__mDataFormatString__ += 'f'
        self.__mRawData__.append(value)
        self.__mDataWritePos__ += 4

    def writeString8(self, valueStr):
        strSize = len(valueStr)
        self.__mDataFormatString__ += (str(strSize) + 's')
        self.__mRawData__.append(valueStr)
        self.__mStringInfo__.append([strSize, self.__mDataWritePos__])
        self.__mStringNo__ += 1
        self.__mDataWritePos__ +=  strSize

    def write(self, formatStr, value):
        if not formatStr.isalpha():
            if formatStr[0] != '=':
                return
            else:
                validFormatStr = formatStr[1:]
        else:
            validFormatStr = formatStr

        self.__mDataFormatString__ += validFormatStr
        if type(value) is types.ListType:
            self.__mRawData__.extend(value)
        else:
            sel.__mRawData__.append(value)

        self.__mObjectInfo__.append([struct.Struct(validFormatStr).size, self.__mDataWritePos__])
        self.__mObjectNo__ += 1
        self.__mDataWritePos__ += struct.Struct(validFormatStr).size

    def writFlatBinder(self, value):
        self.write('IIQQ', value)

    def writeInt32(self, value):
        self.write4Bytes(value)

    def writeUInt32(self, value):
        self.writeInt32(value)

    def writeInt64(self, value):
        self.write8Bytes(value)

    def writeUInt64(self, value):
        self.writeInt64(value)

    def submitWrite(self):
        parcelFormat = struct.Struct(self.__mDataFormatString__)
        self.__mDataSize__ = parcelFormat.size
        self.__mData__ = ctypes.create_string_buffer(self.__mDataSize__)
        print "submitWrite formatStr: ", self.__mDataFormatString__
        print "submitWrite DataValue: ", self.__mRawData__
        parcelFormat.pack_into(self.__mData__, 0, *tuple(self.__mRawData__))


    def allocMemory(self, size):
        self.__mData__ = ctypes.create_string_buffer(size)

    def readByte(self):
        if self.__mDataReadPos__ + 1 > self.__mDataSize__:
            return

        s = struct.Struct('b')
        ret = s.unpack_from(self.__mData__, self.__mDataReadPos__)
        self.__mDataReadPos__ += 1
        if ret[0] == None:
            return
        return ret[0]

    def read2Bytes(self):
        if self.__mDataReadPos__ + 2 > self.__mDataSize__:
            return
        s = struct.Struct('h')
        ret = s.unpack_from(self.__mData__, self.__mDataReadPos__)
        self.__mDataReadPos__ += 2
        if ret[0] == None:
            return
        return ret[0]

    def read4Bytes(self):
        if self.__mDataReadPos__ + 4 > self.__mDataSize__:
            return
        s = struct.Struct('I')
        ret = s.unpack_from(self.__mData__, self.__mDataReadPos__)
        self.__mDataReadPos__ += 4
        if ret[0] == None:
            return
        return ret[0]

    def read8Bytes(self):
        if self.__mDataReadPos__ + 8 > self.__mDataSize__:
            return
        s = struct.Struct('Q')
        ret = s.unpack_from(self.__mData__, self.__mDataReadPos__)
        self.__mDataReadPos__ += 8
        if ret[0] == None:
            return
        return ret[0]

    def readFloat(self, value):
        f = self.read4Bytes()
        if f[0] != None:
            return float(f[0])

    def readString8(self):
        retStrInfo = self.__mStringInfo__[self.__mStringReadNo__]
        strSize = retStrInfo[0]
        strReadPos = retStrInfo[1]

        if self.__mDataReadPos__ + strSize > self.__mDataSize__:
            return
        s = struct.Struct( str(strSize) + 's')
        ret = s.unpack_from(self.__mData__, strReadPos)
        self.__mStringReadNo__ += 1
        self.__mDataReadPos__ += strSize
        if ret[0] == None:
            return
        return str(ret[0])

    def readInt32(self):
        ret = self.read4Bytes()
        if ret is not None:
            return int(ret)

    def readUInt32(self):
        return self.readInt32()

    def readInt64(self):
        ret = self.read8Bytes()
        if ret is not None:
            return int(ret)

    def readUInt64(self):
        return self.readInt64()

    def setDataSize(self, size):
        self.__mDataSize__ = size

    def setDataReadPos(self, pos):
        self.__mDataReadPos__ = pos

    def ipcDataSize(self):
        return self.__mDataSize__

    def ipcData(self):
        return ctypes.addressof(self.__mData__)

    def dump(self):
        print "FormatString: ", self.__mDataFormatString__
        print "Value: ", self.__mRawData__[0]
