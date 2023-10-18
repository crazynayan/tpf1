import os
from typing import Set

from p5_v3.p01_errors import SourceFileNotFound

base_data_macro_path = "p0_source/base/macro/"
base_asm_path = "p0_source/base/asm/"
asm_extension = ".asm"
macro_extension = ".mac"

client_domain = "sabre"


def get_client_domain() -> str:
    return client_domain


def get_domain_path():
    return f"p0_source/{get_client_domain()}"

def get_domain_macro_path() -> str:
    return f"{get_domain_path()}/macro/"


def get_domain_asm_path() -> str:
    return f"{get_domain_path()}/asm/"


def get_data_macros_from_path(file_path: str) -> Set[str]:
    return {filename[:-4].upper() for filename in os.listdir(file_path) if filename.endswith(macro_extension)}


def get_asm_from_path(file_path: str) -> Set[str]:
    return {filename[:4].upper() for filename in os.listdir(file_path) if filename.endswith(asm_extension) and len(filename) >= 8}


def get_file_path_from_seg_name(seg_name: str, version: str = str()):
    filename = f"{seg_name.lower()}{version.lower()}{asm_extension}"
    file_path = f"{get_domain_asm_path()}{filename}"
    if os.path.exists(file_path):
        return file_path
    file_path = f"{base_asm_path}{filename}"
    if os.path.exists(file_path):
        return file_path
    raise SourceFileNotFound


base_data_macros: Set[str] = get_data_macros_from_path(base_data_macro_path)
base_asm: Set[str] = get_asm_from_path(base_asm_path)
client_domain_data_macros: Set[str] = get_data_macros_from_path(get_domain_macro_path())
client_domain_asm: Set[str] = get_asm_from_path(get_domain_asm_path())
all_data_macros: Set[str] = client_domain_data_macros | base_data_macros
all_asm: Set[str] = client_domain_asm | base_asm


def update_client_domain(new_client_domain: str) -> None:
    global client_domain, all_data_macros, client_domain_data_macros, all_asm, client_domain_asm
    client_domain = new_client_domain
    client_domain_data_macros = get_data_macros_from_path(get_domain_macro_path())
    client_domain_asm = get_asm_from_path(get_domain_asm_path())
    all_data_macros = client_domain_data_macros | base_data_macros
    all_asm = client_domain_asm | base_asm


def get_data_macros() -> Set[str]:
    return all_data_macros


def is_data_macro_valid(data_macro_name: str) -> bool:
    return data_macro_name in get_data_macros()


def get_data_macro_file_path(data_macro_name: str) -> str:
    filename = data_macro_name.lower() + ".mac"
    return get_domain_macro_path() + filename if data_macro_name in client_domain_data_macros else base_data_macro_path + filename


