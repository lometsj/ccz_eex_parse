import struct


def u32(data):
    return struct.unpack("<I", data)[0]


def u16(data):
    return struct.unpack("<H", data)[0]


def u8(data):
    return struct.unpack("<B", data)[0]

