import random
from typing import Dict, Optional

from p1_utils.errors import FaceError, FileError


class FlatFile:
    DB: Dict[str, bytearray] = dict()

    @classmethod
    def init_db(cls):
        cls.DB = dict()

    @classmethod
    def get_new_pool_address(cls) -> str:
        for _ in range(1000):
            pool_address = random.choice(range(0x80000000, 0x100000000))
            pool_key = f"{pool_address:08X}"
            if pool_key not in cls.DB:
                return pool_key
        raise FileError

    @classmethod
    def get_record(cls, file_address: int) -> Optional[bytearray]:
        db_key = f"{file_address:08X}"
        if db_key not in cls.DB:
            return None
        return cls.DB[db_key]

    @classmethod
    def add_fixed(cls, data: bytearray, face_type: int, ordinal: int) -> None:
        file_address = cls.face(face_type, ordinal)
        cls.DB[file_address] = data

    @classmethod
    def add_pool(cls, data: bytearray) -> int:
        db_key = cls.get_new_pool_address()
        cls.DB[db_key] = data
        return int(db_key, 16)

    @classmethod
    def set_data(cls, data: bytearray, file_address: int) -> None:
        db_key = f"{file_address:08X}"
        try:
            cls.DB[db_key] = data
        except KeyError:
            raise FileError

    @classmethod
    def remove_pool(cls, file_address: int):
        db_key = f"{file_address:08X}"
        if db_key in cls.DB:
            del cls.DB[db_key]
        return

    @staticmethod
    def face(face_type: int, ordinal: int) -> str:
        if face_type < 0x7F and ordinal < 0xFFFFFF:
            file_address = f"{face_type:02X}{ordinal:06X}"
        elif face_type < 0x7FFF and ordinal < 0xFFFF:
            file_address = f"{face_type:04X}{ordinal:04X}"
        elif face_type < 0x7FFFFF and ordinal < 0xFF:
            file_address = f"{face_type:06X}{ordinal:02X}"
        else:
            raise FaceError
        return file_address
