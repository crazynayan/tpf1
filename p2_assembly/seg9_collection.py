import os
from typing import Dict, Optional, List, Tuple

from firestore_ci import FirestoreDocument
# noinspection PyPackageRequirements
from google.cloud.storage import Client

from config import config
from p2_assembly.seg6_segment import Segment


class SegLst(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()
        self.file_type: str = str()
        self.filename: str = str()
        self.source: str = str()
        self.blob_name: str = str()
        self.error_line: str = str()
        self.error_constant: str = str()
        self.loc: int = int()
        self.error_count: int = int()
        self.error_cmds: List[str] = list()

    def __repr__(self):
        return f"{self.seg_name}:{self.file_type}:{self.loc}:E{self.error_count}"

    @property
    def execution_percentage(self) -> str:
        return f"{(self.loc - self.error_count) * 100 // self.loc if self.loc > 0 else 0}%"

    @property
    def assembly_error(self) -> str:
        return self.error_line or self.error_constant


SegLst.init("segments")


def read_folder(folder_name: str, extensions: set) -> List[Tuple[str, str]]:
    # Returns a list of seg_name and filename
    return [(filename[:4].upper(), os.path.join(folder_name, filename)) for filename in os.listdir(folder_name)
            if len(filename) >= 6 and filename[-4:].lower() in extensions]


def read_cloud() -> List[Tuple[str, str]]:
    # Returns a list of blob_name and filename
    client = Client()
    blobs = client.list_blobs(config.BUCKET)
    blob_list = [(blob.name, os.path.join(config.DOWNLOAD_PATH, blob.name)) for blob in blobs]
    client.close()
    return blob_list


def get_segment(seg_name: str, filename: str, file_type: str, source: str, blob_name: Optional[str] = None) -> Segment:
    segment: Segment = Segment(seg_name, filename)
    segment.file_type = file_type
    segment.source = source
    segment.blob_name = blob_name if blob_name else str()
    return segment


class _SegmentCollection:

    def __init__(self):
        self.segments: Dict = dict()  # Dictionary of Segment. Segment name is the key.
        if config.CI_CLOUD_STORAGE:
            self.init_seg_from_db()
        else:
            self.init_seg_from_folder(config.ASM_FOLDER_NAME, config.ASM_EXT, config.ASM)
            self.init_seg_from_folder(config.LXP_FOLDER_NAME, config.LXP_EXT, config.LST)

    def init_seg_from_folder(self, folder_name: str, extensions: set, file_type: str):
        for seg_name, filename in read_folder(folder_name, extensions):
            self.segments[seg_name]: Segment = get_segment(seg_name, filename, file_type, config.LOCAL)
        return

    def init_seg_from_db(self):
        self.segments: Dict = dict()  # Ensure segments is empty
        seg_lst: List[SegLst] = SegLst.objects.get()
        for seg in seg_lst:
            self.init_seg_from_seg_lst(seg)
        return

    def init_seg_from_seg_lst(self, seg: SegLst):
        self.segments[seg.seg_name]: Segment = get_segment(seg.seg_name, seg.filename, seg.file_type, seg.source,
                                                           seg.blob_name)

    def init_from_cloud(self, blob_name: str) -> str:
        seg_name = blob_name[:4].upper()
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        self.segments[seg_name] = get_segment(seg_name, filename, config.LST, config.CLOUD, blob_name)
        return seg_name

    def from_asm_to_lst(self, seg_name, blob_name) -> Optional[Segment]:
        seg_key = seg_name.upper()
        asm_seg: Segment = self.get_seg(seg_key)
        if not asm_seg:
            return None
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        self.segments[seg_key] = get_segment(seg_key, filename, config.LST, config.CLOUD, blob_name)
        return self.segments[seg_key]

    def is_seg_present(self, seg_name: str) -> bool:
        if not config.CI_CLOUD_STORAGE:
            return seg_name in self.segments
        if seg_name in self.segments:
            return True
        seg: SegLst = SegLst.objects.filter_by(seg_name=seg_name).first()
        if not seg:
            return False
        self.init_seg_from_seg_lst(seg)
        return True

    def get_seg(self, seg_name) -> Optional[Segment]:
        if not self.is_seg_present(seg_name):
            return None
        return self.segments[seg_name]

    def is_seg_local(self, seg_name) -> bool:
        if not self.is_seg_present(seg_name):
            return False
        return self.segments[seg_name].source == config.LOCAL


seg_collection = _SegmentCollection()
