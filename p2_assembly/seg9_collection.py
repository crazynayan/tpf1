import os
from typing import Dict, Optional

from config import config
from p2_assembly.seg6_segment import Segment


class _SegmentCollection:
    ASM_EXT = {".asm", ".txt"}
    ASM_FOLDER_NAME = os.path.join(config.ROOT_DIR, "p0_source", "asm")
    LST_EXT = {".lst"}
    LST_FOLDER_NAME = os.path.join(config.ROOT_DIR, "p0_source", "lst")

    def __init__(self):
        self.segments: Dict = dict()  # Dictionary of Segment. Segment name is the key.
        self.init_segments(self.ASM_FOLDER_NAME, self.ASM_EXT, config.ASM)
        self.init_segments(self.LST_FOLDER_NAME, self.LST_EXT, config.LST)
        self.init_all_from_cloud()

    def init_segments(self, folder_name: str, extensions: set, file_type: str):
        for file_name in os.listdir(folder_name):
            if len(file_name) < 6 or file_name[-4:].lower() not in extensions:
                continue
            seg_name = file_name[:4].upper()
            if seg_name in self.segments:
                continue
            file_name = os.path.join(folder_name, file_name)
            self.segments[seg_name]: Segment = Segment(seg_name, file_name)
            self.segments[seg_name].file_type = file_type
        return

    def init_all_from_cloud(self):
        if not config.CI_CLOUD_STORAGE:
            return
        # noinspection PyPackageRequirements
        from google.cloud.storage import Client
        client = Client()
        blobs = client.list_blobs(config.BUCKET)
        for blob in blobs:
            self.init_from_cloud(blob.name)
        client.close()
        return

    def init_from_cloud(self, blob_name: str):
        seg_name = blob_name[:4].upper()
        if seg_name in self.segments and self.segments[seg_name].source == config.LOCAL:
            return
        filename = os.path.join(config.DOWNLOAD_PATH, blob_name)
        segment = Segment(seg_name, filename)
        segment.file_type = config.LST
        segment.source = config.CLOUD
        segment.blob_name = blob_name
        self.segments[seg_name] = segment

    def is_seg_present(self, seg_name: str) -> bool:
        if not config.CI_CLOUD_STORAGE:
            return seg_name in self.segments
        if seg_name in self.segments:
            return True
        self.init_all_from_cloud()
        return seg_name in self.segments

    def get_seg(self, seg_name) -> Optional[Segment]:
        if not self.is_seg_present(seg_name):
            return None
        return self.segments[seg_name]

    def get_all_segments(self) -> Dict:
        if config.CI_CLOUD_STORAGE:
            self.init_all_from_cloud()
        return self.segments

    def is_seg_local(self, seg_name) -> bool:
        if not self.is_seg_present(seg_name):
            return False
        return self.segments[seg_name].source == config.LOCAL


seg_collection = _SegmentCollection()
