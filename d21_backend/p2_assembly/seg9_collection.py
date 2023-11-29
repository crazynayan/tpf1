import os
from typing import Dict, Optional, List, Tuple

from firestore_ci import FirestoreDocument
# noinspection PyPackageRequirements
from google.cloud.storage import Client

from d21_backend.config import config
from d21_backend.p1_utils.domain import read_folder, get_domain_folder, get_base_folder, get_domain, get_bucket
from d21_backend.p2_assembly.seg6_segment import Segment


class SegLst(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()
        self.file_type: str = str()
        self.filename: str = str()
        self.domain: str = str()
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


def read_cloud() -> List[Tuple[str, str]]:
    # Returns a list of blob_name and filename
    client = Client()
    blobs = client.list_blobs(get_bucket())
    blob_list = [(blob.name, os.path.join(config.DOWNLOAD_PATH, blob.name)) for blob in blobs]
    client.close()
    return blob_list


def get_segment(seg_name: str, filename: str, file_type: str, source: str, blob_name: Optional[str] = None) -> Segment:
    segment: Segment = Segment(seg_name, filename)
    segment.file_type = file_type
    segment.source = source
    segment.blob_name = blob_name if blob_name else str()
    return segment


def get_seg_lst_for_domain() -> List[SegLst]:
    domains: List[str] = [config.DOMAINS.BASE, get_domain()]
    seg_lst: List[SegLst] = SegLst.objects.filter("domain", SegLst.objects.IN, domains).get()
    seg_lst.sort(key=lambda item: (item.domain, item.file_type), reverse=True)  # Assumes all domains are > base
    return seg_lst


class SegmentCollection:

    def __init__(self):
        self.segments: Dict = dict()  # Dictionary of Segment. Segment name is the key.
        self.domain: str = get_domain()
        if config.CI_CLOUD_STORAGE:
            self.init_seg_from_db()
        else:
            self.init_seg_from_folder(get_domain_folder(config.LXP), config.LXP_EXT, config.LST)
            self.init_seg_from_folder(get_base_folder(config.LXP), config.LXP_EXT, config.LST)
            self.init_seg_from_folder(get_domain_folder(config.ASM), config.ASM_EXT, config.ASM)
            self.init_seg_from_folder(get_base_folder(config.ASM), config.ASM_EXT, config.ASM)

    @staticmethod
    def filename_parser(filename: str):
        return filename[:4].upper()

    def init_seg_from_folder(self, folder_name: str, extensions: set, file_type: str):
        for seg_name, filename in read_folder(folder_name, extensions, self.filename_parser):
            if seg_name in self.segments:
                continue
            self.segments[seg_name]: Segment = get_segment(seg_name, filename, file_type=file_type, source=config.LOCAL)
        return

    def init_seg_from_db(self):
        self.segments: Dict = dict()  # Ensure segments is empty
        seg_lst: List[SegLst] = get_seg_lst_for_domain()
        for seg in seg_lst:
            if seg.seg_name in self.segments:
                continue
            self.init_seg_from_seg_lst(seg)
        return

    def init_seg_from_seg_lst(self, seg: SegLst):
        self.segments[seg.seg_name]: Segment = get_segment(seg.seg_name, seg.filename, seg.file_type, seg.source,
                                                           seg.blob_name)

    def init_from_cloud(self, blob_name: str, file_type) -> str:
        seg_name = blob_name[:4].upper()
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        self.segments[seg_name] = get_segment(seg_name, filename, source=config.CLOUD, file_type=file_type,
                                              blob_name=blob_name)
        return seg_name

    def from_asm_to_lst(self, seg_name, blob_name) -> Optional[Segment]:
        seg_key = seg_name.upper()
        asm_seg: Segment = self.get_seg(seg_key)
        if not asm_seg:
            return None
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        self.segments[seg_key] = get_segment(seg_key, filename, source=config.CLOUD, file_type=config.LST,
                                             blob_name=blob_name)
        return self.segments[seg_key]

    def is_seg_present(self, seg_name: str) -> bool:
        if not config.CI_CLOUD_STORAGE:
            return seg_name in self.segments
        if seg_name in self.segments:
            return True
        seg: SegLst = next((seg_lst for seg_lst in get_seg_lst_for_domain() if seg_lst.seg_name == seg_name), None)
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


_seg_collection = SegmentCollection()


def get_seg_collection() -> SegmentCollection:
    return _seg_collection


def init_seg_collection() -> None:
    global _seg_collection
    if _seg_collection.domain != get_domain():
        _seg_collection = SegmentCollection()
    return
