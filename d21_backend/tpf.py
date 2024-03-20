import os
from typing import List

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-tokyo.json"
# noinspection PyPackageRequirements
from google.cloud.storage import Client

from d21_backend.config import config
from d21_backend.p1_utils.data_type import DataType
from d21_backend.p1_utils.domain import get_bucket, get_domain_folder, is_domain_valid, get_folder_by_domain, get_base_folder
from d21_backend.p1_utils.ucdr import date_to_pars, pars_to_date
from d21_backend.p2_assembly.seg6_segment import Segment
from d21_backend.p2_assembly.seg8_listing import LstCmd, create_lxp
from d21_backend.p2_assembly.seg9_collection import SegLst, get_segment, get_seg_collection
from d21_backend.p7_flask_app.segment import get_seg_lst, reset_seg_assembly


def to_pars(date: str):
    date_bytes = DataType("C", input=date).to_bytes()
    pars = date_to_pars(date_bytes)[0]
    print(f"{pars:X}")


def from_pars(pars: int):
    date_bytes = pars_to_date(pars, full_year=True)
    date = DataType("C", bytes=date_bytes).decode
    print(date)


# def init_seg_lst():
#     SegLst.objects.delete()
#     seg_to_create: List[SegLst] = list()
#     lxp_set: set = set()
#     for seg_name, filename in read_folder(config.ASM_FOLDER_NAME, config.ASM_EXT):
#         segment = get_segment(seg_name, filename, config.ASM, config.LOCAL)
#         seg_to_create.append(get_seg_lst(segment))
#     for seg_name, filename in read_folder(config.LXP_FOLDER_NAME, config.LXP_EXT):
#         segment = get_segment(seg_name, filename, config.LST, config.LOCAL)
#         seg_to_create.append(get_seg_lst(segment))
#         lxp_set.add(seg_name)
#     for blob_name, filename in read_cloud():
#         segment = get_segment(blob_name[:4].upper(), filename, config.LST, config.CLOUD, blob_name)
#         if segment.seg_name not in lxp_set:
#             seg_to_create.append(get_seg_lst(segment))
#     SegLst.objects.create_all(SegLst.objects.to_dicts(seg_to_create))


def reset_and_create_lxp(blob_name: str):
    seg = reset_seg_assembly(blob_name, config.LST)
    if not seg:
        print("Reset fail")
        return
    if create_lxp(seg.seg_name):
        seg_lst = SegLst.objects.filter_by(seg_name=seg.seg_name).first()
        seg_lst.source = config.LOCAL
        seg_lst.save()
        print("LXP created")
    else:
        print("Error in creating LXP")
    return


def init_asm_seg(filename: str, base: bool = False):
    seg_name: str = filename[:4].upper()
    folder_path: str = get_domain_folder(config.ASM) if not base else get_base_folder(config.ASM)
    file_path: str = os.path.join(folder_path, filename)
    segment: Segment = get_segment(seg_name, file_path, config.ASM, config.LOCAL)
    seg: SegLst = get_seg_lst(segment)  # Assemble the segment and create LstCmd
    SegLst.objects.filter_by(seg_name=seg_name).delete()
    seg.create()
    return seg


def copy_seg_across_domains(seg_name: str, from_domain: str, to_domain):
    segments = SegLst.objects.filter_by(seg_name=seg_name).get()
    if not segments:
        print(f"{seg_name} not found. Use 4 letter codes in upper case.")
        return
    if not any(segment.domain == from_domain for segment in segments):
        print(f"{seg_name} not present in {from_domain} domain.")
        return
    if any(segment.domain == to_domain for segment in segments):
        print(f"{seg_name} is already present in {to_domain} domain.")
        return
    if not is_domain_valid(to_domain):
        print(f"{to_domain} domain is invalid.")
        return
    filename: str = f"{seg_name.lower()}.asm"
    file_path: str = os.path.join(get_folder_by_domain(config.ASM, to_domain), filename)
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return
    new_segment = get_seg_lst(get_segment(seg_name, file_path, config.ASM, config.LOCAL))
    new_segment.domain = to_domain
    new_segment.create()
    return new_segment


def migrate_to_lst(seg_name: str):
    source_path = os.path.join(get_domain_folder(config.ASM), f"{seg_name}.asm")
    target_path = os.path.join("tmp", f"{seg_name}.asm")
    if os.path.isfile(source_path):
        if not os.path.isfile(target_path):
            os.rename(source_path, target_path)
        else:
            os.remove(source_path)
        print(f"{seg_name} removed from asm source folder.")
    elif not os.path.isfile(target_path):
        print(f"{seg_name}.asm not found.")
        return
    # Upload listing
    filename = f"{seg_name}99.lst"
    source_path = f"/home/nayan/Downloads/{filename}"
    if not os.path.isfile(source_path):
        print(f"Listing of {seg_name} not found in Downloads directory.")
        return
    client = Client()
    blob = client.bucket(get_bucket()).blob(filename)
    blob.upload_from_filename(source_path)
    client.close()
    print(f"{filename} uploaded to Google Cloud Storage.")
    # Generate Listing Commands
    seg: Segment = get_seg_collection().from_asm_to_lst(seg_name, filename)
    if not seg:
        print("Error in creating a segment object.")
        return
    LstCmd.objects.filter_by(seg_name=seg.seg_name).delete()
    seg_lst: SegLst = get_seg_lst(seg)  # Assemble the segment and create LstCmd
    print(f"{seg_name} listing commands generated and filed.")
    # Create LXP
    filename = create_lxp(seg_name)  # From LstCmd
    if not filename:
        print("Error in creating lxp.")
    else:
        print(f"{seg_name} lxp generated and saved.")
        seg_lst.filename = filename
        seg_lst.source = config.LOCAL
    SegLst.objects.filter_by(seg_name=seg.seg_name).delete()
    seg_lst.create()
    return


def update_seg_lst(seg_names: List[str]):
    seg_lst = list()
    config.CI_CLOUD_STORAGE = True
    for seg_name in seg_names:
        segment = get_seg_collection().get_seg(seg_name)
        if not segment:
            print(f"{seg_name} not found.")
            continue
        seg_lst.append(get_seg_lst(segment))
    update_seg_names = [seg.seg_name for seg in seg_lst]
    SegLst.objects.filter("seg_name", SegLst.objects.IN, update_seg_names).delete()
    SegLst.objects.create_all(SegLst.objects.to_dicts(seg_lst))
    print(f"{len(seg_lst)} SegLst updated.")
    return
