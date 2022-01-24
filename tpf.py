import os
from base64 import b64encode
from typing import List, Optional

from config import config
from p2_assembly.seg6_segment import Segment
from p2_assembly.seg8_listing import LstCmd
from p2_assembly.seg9_collection import SegLst, read_folder, get_segment, read_cloud, seg_collection
from p4_execution.ex5_execute import TpfServer

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-tokyo.json"

from p7_flask_app.auth import User


def create_user(email: str, initial: str):
    if not isinstance(email, str) or sum(1 for char in email if char == "@") != 1 or "|" in email:
        print(f"Invalid email - {email}")
        return
    if User.objects.filter_by(email=email).first():
        print(f"Email already exists")
        return
    if not isinstance(initial, str) or len(initial) != 2 or not initial.isalpha():
        print(f"Initial should be 2 character alphabet string")
        return
    if User.objects.filter_by(initial=initial).first():
        print(f"Initial already exits")
        return
    user = User()
    user.email = email
    user.initial = initial.upper()
    password = b64encode(os.urandom(24)).decode()
    user.set_password(password)
    user.set_id(email.replace("@", "_").replace(".", "-"))
    user.save()
    print(f"User {user.email} created with initial {user.initial}. Your password is {password}")
    return


def get_seg_lst(segment: Segment) -> SegLst:
    seg_lst = SegLst()
    seg_lst.seg_name = segment.seg_name
    seg_lst.filename = segment.file_name
    seg_lst.file_type = segment.file_type
    seg_lst.source = segment.source
    seg_lst.blob_name = segment.blob_name
    segment.assemble()
    seg_lst.error_line = str(segment.error_line)
    seg_lst.error_constant = segment.error_constant
    seg_lst.loc = len(segment.nodes)
    unsupported_nodes = [node for _, node in segment.nodes.items()
                         if node.command not in TpfServer().supported_commands]
    seg_lst.error_count = len(unsupported_nodes)
    seg_lst.error_cmds = list({node.command for node in unsupported_nodes})
    return seg_lst


def init_seg_lst():
    SegLst.objects.delete()
    seg_to_create: List[SegLst] = list()
    for seg_name, filename in read_folder(config.ASM_FOLDER_NAME, config.ASM_EXT):
        segment = get_segment(seg_name, filename, config.ASM, config.LOCAL)
        seg_to_create.append(get_seg_lst(segment))
    for seg_name, filename in read_folder(config.LST_FOLDER_NAME, config.LST_EXT):
        segment = get_segment(seg_name, filename, config.LST, config.LOCAL)
        seg_to_create.append(get_seg_lst(segment))
    for blob_name, filename in read_cloud():
        segment = get_segment(blob_name[:4].upper(), filename, config.LST, config.CLOUD, blob_name)
        seg_to_create.append(get_seg_lst(segment))
    SegLst.objects.create_all(SegLst.objects.to_dicts(seg_to_create))


def reset_seg_assembly(blob_name: str) -> Optional[SegLst]:
    seg_name = seg_collection.init_from_cloud(blob_name)
    if not seg_name:
        seg_name = blob_name[:4].upper()
    segment = seg_collection.get_seg(seg_name)
    if not segment:
        return None
    LstCmd.objects.filter_by(seg_name=seg_name).delete()
    SegLst.objects.filter_by(seg_name=seg_name).delete()
    seg: SegLst = get_seg_lst(segment)
    seg.create()
    return seg


def init_asm_seg(filename: str):
    seg_name: str = filename[:4].upper()
    file_path: str = os.path.join(config.ASM_FOLDER_NAME, filename)
    segment: Segment = get_segment(seg_name, file_path, config.ASM, config.LOCAL)
    seg: SegLst = get_seg_lst(segment)
    SegLst.objects.filter_by(seg_name=seg_name).delete()
    seg.create()
    return seg
