##
##  dpc_binary.py
##
##  Binary transport for DPC
##
##  Created by Renat Idrisov on 2022-07-24
##  Copyright (C) 2022 Fungible. All rights reserved.
##

from .dpc_client import DpcEncoder
from typing import Any, Tuple, Union
from .binary_json import *

class BinaryJSONEncoder(DpcEncoder):
    def enable_command(self):
        # type: (Any) -> Union[bytes(), None]
        return b'{"verb":"encoding_binary_json", "tid":0}\n'

    def serialization_size(self, buffer):
        # type: (Any, bytes()) -> int
        size = binary_json.serialization_size(buffer)
        return size if size <= len(buffer) else -1

    def decode(self, buffer):
        # type: (Any, bytes()) -> Any
        return binary_json.decode(buffer)

    def encode(self, data):
        # type: (Any, Any) -> bytes()
        return binary_json.encode(data)

    def blob_from_string(self, data):
        # type: (bytes()) -> Any
        BLOB_CHUNK_SIZE = 32 * 1024
        blob_array = []
        position = 0
        while position < len(data):
            next_position = position + BLOB_CHUNK_SIZE
            blob_array.append(data[position:next_position])
            position = next_position
        return blob_array

    def blob_to_string(self, data):
        # type: (Any) -> bytes()
        result = b''
        for chunk in data:
            result += bytes(bytearray(chunk))
        return result
