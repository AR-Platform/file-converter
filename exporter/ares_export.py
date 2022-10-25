"""Exports the given data as an ARES file."""
from interfaces.export_interface import ExportInterface
from typing import BinaryIO, Optional
from enum import Enum, auto
import struct


# ======================================================================================================================
#            _____  ______  _____     ________   _______   ____  _____ _______
#      /\   |  __ \|  ____|/ ____|   |  ____\ \ / /  __ \ / __ \|  __ \__   __|
#     /  \  | |__) | |__  | (___     | |__   \ V /| |__) | |  | | |__) | | |
#    / /\ \ |  _  /|  __|  \___ \    |  __|   > < |  ___/| |  | |  _  /  | |
#   / ____ \| | \ \| |____ ____) |   | |____ / . \| |    | |__| | | \ \  | |
#  /_/    \_\_|  \_\______|_____/    |______/_/ \_\_|     \____/|_|  \_\ |_|
#
# ======================================================================================================================


class Export(ExportInterface):
    """Export class that contains the ARES file export."""
    def __init__(self):
        self.format_identifier = 0
        self.vertex_amount = 0
        self.vertex_precision = None
        self.polygon = 0
        self.face_amount = 0
        self.connectivity_precision = None
        self.frames = 0
        self.data_blocks = 0

    def supported_formats(self) -> list:
        """Returns the supported formats.

        :return: The supported formats.
        """
        return ["ares"]

    def export(self, data: dict, path: str) -> None:
        """Exports the given data to the desired path.

        :param data: The data to export.
        :param path: The path to export to.
        """
        self.get_mesh_information(data)
        with open('%s.ares' % path, 'wb') as stream:
            self.write_header(stream)
            self.write_mesh(stream, data)
            if "blocks" in data.keys():
                for block in data["blocks"]:
                    self.write_data_block(stream, block)

    def get_mesh_information(self, data: dict) -> None:
        """Fetches all relevant mesh information from the given data dictionary.

        :param data: The data dictionary to fetch the information from.
        """
        self.vertex_amount = len(data["vertices"]) // 3
        self.vertex_precision = BinaryType[data["vertex-precision"]] if "vertex-precision" in data else BinaryType.FP32
        self.polygon = data["polygon"]
        self.face_amount = len(data["connectivity"]) // self.polygon
        self.connectivity_precision = get_smallest_uint(self.vertex_amount)
        self.frames = data["frames"]
        self.data_blocks = len(data["blocks"]) if "blocks" in data else 0

    def write_header(self, stream: BinaryIO) -> None:
        """Writes the ARES header information to the given binary stream.

        :param stream: The binary stream.
        """
        write_binary_single(stream, BinaryType.UINT8, self.format_identifier)
        write_binary_single(stream, BinaryType.UINT32, self.vertex_amount)
        write_binary_single(stream, BinaryType.UINT8, self.polygon)
        write_binary_single(stream, BinaryType.UINT32, self.face_amount)
        write_binary_single(stream, BinaryType.UINT16, self.frames)
        write_binary_single(stream, BinaryType.UINT8, self.data_blocks)

    def write_mesh(self, stream: BinaryIO, data: dict) -> None:
        """Writes the mesh information to the given binary stream.

        :param stream: The binary stream.
        :param data: The data dictionary containing the mesh information.
        """
        write_binary(stream, self.vertex_precision, data["vertices"])
        write_binary(stream, self.connectivity_precision, data["connectivity"])

    def write_data_block(self, stream: BinaryIO, block: dict) -> None:
        """Writes all data of the given block to the binary stream.

        :param stream: The binary stream.
        :param block: The data block dictionary.
        """
        write_binary_single(stream, BinaryType.UINT8, len(block["name"]))
        write_binary_string(stream, block["name"])
        write_binary_single(stream, BinaryType.UINT8, block["precision"])
        write_binary_single(stream, BinaryType.BOOL, (len(block["values"]) / self.vertex_amount) == 1)
        binary_type = BinaryType.UINT8 if (block["precision"] == 12) else BinaryType((block["precision"]) + 1)
        write_binary(stream, binary_type, block["values"])


# ======================================================================================================================
#    ____ _____ _   _          _______     __    _____  ______ ______ _____ _   _ _____ _______ _____ ____  _   _  _____
#  |  _ \_   _| \ | |   /\   |  __ \ \   / /   |  __ \|  ____|  ____|_   _| \ | |_   _|__   __|_   _/ __ \| \ | |/ ____|
#  | |_) || | |  \| |  /  \  | |__) \ \_/ /    | |  | | |__  | |__    | | |  \| | | |    | |    | || |  | |  \| | (___
#  |  _ < | | | . ` | / /\ \ |  _  / \   /     | |  | |  __| |  __|   | | | . ` | | |    | |    | || |  | | . ` |\___ \
#  | |_) || |_| |\  |/ ____ \| | \ \  | |      | |__| | |____| |     _| |_| |\  |_| |_   | |   _| || |__| | |\  |____) |
#  |____/_____|_| \_/_/    \_\_|  \_\ |_|      |_____/|______|_|    |_____|_| \_|_____|  |_|  |_____\____/|_| \_|_____/
#
# ======================================================================================================================
# region Binary Definitions

class BinaryType(Enum):
    """Binary types."""
    BOOL = auto()
    UINT8 = auto()
    UINT16 = auto()
    UINT32 = auto()
    UINT64 = auto()
    INT8 = auto()
    INT16 = auto()
    INT32 = auto()
    INT64 = auto()
    FP16 = auto()
    FP32 = auto()
    FP64 = auto()


format_string_single = {
    BinaryType.BOOL: "<?",
    BinaryType.UINT8: "<B",
    BinaryType.UINT16: "<H",
    BinaryType.UINT32: "<I",
    BinaryType.UINT64: "<Q",
    BinaryType.INT8: "<b",
    BinaryType.INT16: "<h",
    BinaryType.INT32: "<i",
    BinaryType.INT64: "<q",
    BinaryType.FP16: "<e",
    BinaryType.FP32: "<f",
    BinaryType.FP64: "<d"
}

format_string = {
    BinaryType.BOOL: "<%s?",
    BinaryType.UINT8: "<%sB",
    BinaryType.UINT16: "<%sH",
    BinaryType.UINT32: "<%sI",
    BinaryType.UINT64: "<%sQ",
    BinaryType.INT8: "<%sb",
    BinaryType.INT16: "<%sh",
    BinaryType.INT32: "<%si",
    BinaryType.INT64: "<%sq",
    BinaryType.FP16: "<%se",
    BinaryType.FP32: "<%sf",
    BinaryType.FP64: "<%sd"
}


# endregion


# ======================================================================================================================
#   ____ _____ _   _          _______     __    ______ _    _ _   _  _____ _______ _____ ____  _   _  _____
#  |  _ \_   _| \ | |   /\   |  __ \ \   / /   |  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
#  | |_) || | |  \| |  /  \  | |__) \ \_/ /    | |__  | |  | |  \| | |       | |    | || |  | |  \| | (___
#  |  _ < | | | . ` | / /\ \ |  _  / \   /     |  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \
#  | |_) || |_| |\  |/ ____ \| | \ \  | |      | |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
#  |____/_____|_| \_/_/    \_\_|  \_\ |_|      |_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/
#
# ======================================================================================================================
# region Binary Functions


def get_smallest_uint(value: int) -> Optional[BinaryType]:
    """Returns the smallest unsigned int BinaryType that contains the given value.

    :param value: The value used to determine the required BinaryType.
    :return: The smallest possible BinaryType to fit the given value.
    """
    if value >= 0:
        if value <= 255:
            return BinaryType.UINT8
        elif value <= 65535:
            return BinaryType.UINT16
        elif value <= 4294967295:
            return BinaryType.UINT32
        elif value <= 18446744073709551615:
            return BinaryType.UINT64
    return None


def get_smallest_int(value: int) -> Optional[BinaryType]:
    """Returns the smallest signed int BinaryType that contains the given value.

    :param value: The value used to determine the required BinaryType.
    :return: The smallest possible BinaryType to fit the given value.
    """
    if -128 <= value < 128:
        return BinaryType.INT8
    elif -32768 <= value < 32768:
        return BinaryType.INT16
    elif -2147483648 <= value < 2147483648:
        return BinaryType.INT32
    elif -9223372036854775808 <= value < 9223372036854775808:
        return BinaryType.INT64
    return None


def write_binary_single(stream: BinaryIO, binary_type: BinaryType, value):
    """Writes a single value with the specified BinaryType to the binary stream.

    :param stream: The binary stream to write the data to.
    :param binary_type: The desired BinaryType.
    :param value: The data as a single value.
    """
    stream.write(struct.pack(format_string_single[binary_type], value))


def write_binary(stream: BinaryIO, binary_type: BinaryType, values: list):
    """Writes the values with the specified BinaryType to the binary stream.

    :param stream: The binary stream to write the data to.
    :param binary_type: The desired BinaryType.
    :param values: The data as a list of values.
    """
    stream.write(struct.pack(format_string[binary_type] % len(values), *values))


def write_binary_string(stream: BinaryIO, value: str):
    """Writes the given string to the binary stream.

    :param stream: The binary stream to write the data to.
    :param value: The string.
    """
    stream.write(bytes(value, encoding="ascii"))

# endregion
