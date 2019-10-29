from typing import Dict, Optional


class FlatFile:
    DB: Dict[str, bytearray] = dict()
    POOL: Dict[str, int] = dict()

    @classmethod
    def get_record(cls, record_id: int, file_address: int) -> Optional[bytearray]:
        db_key = f"{record_id:04X}{file_address:08X}"
        if db_key not in cls.DB:
            return None
        return cls.DB[db_key]

    @classmethod
    def add_fixed(cls, data: bytearray, record_id: int, face_type: int, ordinal: int) -> None:
        file_address = cls.face(face_type, ordinal)
        db_key = f"{record_id:04X}{file_address}"
        cls.DB[db_key] = data

    @classmethod
    def add_pool(cls, data: bytearray, record_id: int) -> int:
        record_id = f"{record_id:04X}"
        cls.POOL[record_id] = cls.POOL[record_id] + 1 if record_id in cls.POOL else 1
        file_address = cls.POOL[record_id]
        db_key = f"{record_id}{file_address:08X}"
        cls.DB[db_key] = data
        return file_address

    @classmethod
    def remove_pool(cls, record_id: int, file_address: int):
        db_key = f"{record_id:04X}{file_address:08X}"
        if db_key in cls.DB:
            del cls.DB[db_key]
        return

    @staticmethod
    def face(face_type: int, ordinal: int) -> str:
        if face_type < 0xFF and ordinal < 0xFFFFFF:
            file_address = f"{face_type:02X}{ordinal:06X}"
        elif face_type < 0xFFFF and ordinal < 0xFFFF:
            file_address = f"{face_type:04X}{ordinal:04X}"
        elif face_type < 0xFFFFFF and ordinal < 0xFF:
            file_address = f"{face_type:06X}{ordinal:02X}"
        else:
            raise TypeError
        return file_address
