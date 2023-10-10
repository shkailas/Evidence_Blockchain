import struct
import uuid
import hashlib as hash

class Block:
    HEADER_FORMAT = struct.Struct("32s d 16s I 12s I")
    HEADER_SIZE = HEADER_FORMAT.size 

    def __init__(self, previous_hash, timestamp, case_id, item_id, state, data_length, data):
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.case_id = uuid.UUID(case_id)
        self.item_id = int(item_id)
        self.state = state
        self.data = data
        self.data_length = data_length 
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        packed_header = self.HEADER_FORMAT.pack(
            self.previous_hash,
            self.timestamp,
            self.case_id.bytes,
            self.item_id,
            str.encode(self.state),
            self.data_length
        )
        packed_data = str.encode(self.data)
        packed_message = packed_header + packed_data
        return hash.sha256(packed_message).digest()

    def pack(self):
        packed_header = self.HEADER_FORMAT.pack(
            self.previous_hash,
            self.timestamp,
            self.case_id.bytes,
            self.item_id,
            str.encode(self.state),
            self.data_length
        )
        return packed_header + str.encode(self.data)

    @classmethod
    def unpack(cls, packed_block):
        header = cls.HEADER_FORMAT.unpack(packed_block[:cls.HEADER_FORMAT.size])
        data_length = header[5]
        data = packed_block[cls.HEADER_FORMAT.size:cls.HEADER_FORMAT.size+data_length]
        block = cls(
            header[0],
            header[1],
            str(uuid.UUID(bytes=header[2])),
            header[3],
            header[4].decode(),
            data_length,
            data.decode(),
        )
        return block


