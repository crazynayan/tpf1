import os
from typing import List, Tuple, Callable

from flask import g

from d21_backend.config import config


def get_domain():
    try:
        return g.current_user.domain
    except (RuntimeError, AttributeError):
        return config.DOMAIN


def get_domain_folder(sub_folder_name: str) -> str:
    return os.path.join(config.SOURCES_ROOT, get_domain(), sub_folder_name)


def get_folder_by_domain(sub_folder_name: str, domain: str) -> str:
    return os.path.join(config.SOURCES_ROOT, domain, sub_folder_name)


def get_base_folder(sub_folder_name: str) -> str:
    return os.path.join(config.SOURCES_ROOT, config.DOMAINS.BASE, sub_folder_name)


def read_folder(folder_name: str, extensions: set, filename_parser: Callable) -> List[Tuple[str, str]]:
    # Returns a list of seg_name and filename
    return [(filename_parser(filename), os.path.join(folder_name, filename)) for filename in os.listdir(folder_name)
            if len(filename) >= 6 and filename[-4:].lower() in extensions]


def get_bucket() -> str:
    domain = get_domain()
    if domain == config.DOMAINS.TIGER:
        return config.BUCKETS.TIGER
    elif domain == config.DOMAINS.SML:
        return config.BUCKETS.SML
    return config.BUCKETS.GENERAL


def is_domain_valid(domain: str) -> bool:
    return domain in config.DOMAINS.__dict__.values()
