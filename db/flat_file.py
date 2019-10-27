from typing import Dict, Optional


class FlatFile:
    DB: Dict[str, bytearray] = list()

    @classmethod
    def get_record(cls, record_id: int, file_address: int) -> Optional[bytearray]:
        db_key = f"{record_id:04X}{file_address:08X}"
        if db_key not in cls.DB:
            return None
        return cls.DB[db_key]

    @classmethod
    def add_fixed(cls, data: bytearray, record_id: int, face_type: int, ordinal: int):
        if face_type < 0xFF and ordinal < 0xFFFFFF:
            file_address = f"{face_type:02X}{ordinal:06X}"
        elif face_type < 0xFFFF and ordinal < 0xFFFF:
            file_address = f"{face_type:04X}{ordinal:04X}"
        elif face_type < 0xFFFFFF and ordinal < 0xFF:
            file_address = f"{face_type:06X}{ordinal:02X}"
        else:
            raise TypeError
        db_key = f"{record_id:04X}{file_address}"
        cls.DB[db_key] = data
