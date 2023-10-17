import os
from typing import Set

base_data_macro_path = "p0_source/base/macro/"

client_domain = "sabre"


def get_domain_macro_path() -> str:
    return f"p0_source/{client_domain}/macro/"


def get_data_macros_from_path(file_path: str) -> Set[str]:
    return {filename[:-4].upper() for filename in os.listdir(file_path) if filename.endswith(".mac")}


base_data_macros: Set[str] = get_data_macros_from_path(base_data_macro_path)
client_domain_data_macros: Set[str] = get_data_macros_from_path(get_domain_macro_path())
all_data_macros: Set[str] = client_domain_data_macros | base_data_macros


def update_client_domain(new_client_domain: str) -> None:
    global client_domain, all_data_macros, client_domain_data_macros
    client_domain = new_client_domain
    client_domain_data_macros = get_data_macros_from_path(get_domain_macro_path())
    all_data_macros = client_domain_data_macros | base_data_macros


def get_data_macros() -> Set[str]:
    return all_data_macros


def is_data_macro_valid(data_macro_name: str) -> bool:
    return data_macro_name in get_data_macros()


def get_data_macro_file_path(data_macro_name: str) -> str:
    filename = data_macro_name.lower() + ".mac"
    return get_domain_macro_path() + filename if data_macro_name in client_domain_data_macros else base_data_macro_path + filename


def get_client_domain() -> str:
    return client_domain
