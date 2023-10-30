import os
from itertools import product
from typing import List, Type

from munch import Munch

from p5_v3.p00_config import FileTag
from p5_v3.p01_errors import DomainError, SourceFileNotFound
from p5_v3.p04_file import FilePath


class ClientDomainCollection:
    CLIENTS = Munch()
    DOMAINS = Munch()
    CLIENT_DOMAIN = Munch()
    ROOT_SOURCE_FOLDER_NAME = "d30_source"
    GENERAL_CLIENT_NAME = "general"
    GENERAL_DOMAIN_NAME = GENERAL_CLIENT_NAME
    BASE_DOMAIN_NAME = "base"
    USER_DEFINED_OPERATION_CODE_CLASS_TAG = "user_defined_operation_code_class"
    BASE_SEGMENT_LIST_TAG = "base_segment_list"
    BASE_MACRO_LIST_TAG = "base_macro_list"
    DOMAIN_SEGMENT_LIST_TAG = "domain_segment_list"
    DOMAIN_MACRO_LIST_TAG = "domain_macro_list"


class ClientDomain:

    def __init__(self, client_name: str = str(), domain_name: str = str()):
        if client_name not in ClientDomainCollection.CLIENT_DOMAIN or domain_name not in ClientDomainCollection.CLIENT_DOMAIN[client_name]:
            raise DomainError
        self.client = client_name if client_name else ClientDomainCollection.GENERAL_CLIENT_NAME
        self.domain = domain_name if domain_name else ClientDomainCollection.GENERAL_DOMAIN_NAME

    def get_domain_path(self):
        return os.path.join(ClientDomainCollection.ROOT_SOURCE_FOLDER_NAME, self.client.lower(), self.domain.lower())

    @staticmethod
    def get_base_path():
        return os.path.join(ClientDomainCollection.ROOT_SOURCE_FOLDER_NAME, ClientDomainCollection.GENERAL_CLIENT_NAME,
                            ClientDomainCollection.BASE_DOMAIN_NAME)

    def get_user_defined_operation_code_class(self) -> Type[object]:
        try:
            return ClientDomainCollection.CLIENT_DOMAIN[self.client][self.domain][
                ClientDomainCollection.USER_DEFINED_OPERATION_CODE_CLASS_TAG]
        except KeyError:
            raise DomainError

    def get_base_segment_list(self) -> List[str]:
        return ClientDomainCollection.CLIENT_DOMAIN[self.client][self.domain][ClientDomainCollection.BASE_SEGMENT_LIST_TAG]

    def get_base_macro_list(self) -> List[str]:
        return ClientDomainCollection.CLIENT_DOMAIN[self.client][self.domain][ClientDomainCollection.BASE_MACRO_LIST_TAG]

    def get_domain_segment_list(self) -> List[str]:
        return ClientDomainCollection.CLIENT_DOMAIN[self.client][self.domain][ClientDomainCollection.DOMAIN_SEGMENT_LIST_TAG]

    def get_domain_macro_list(self) -> List[str]:
        return ClientDomainCollection.CLIENT_DOMAIN[self.client][self.domain][ClientDomainCollection.DOMAIN_MACRO_LIST_TAG]

    def get_segment_list(self) -> List[str]:
        return list(set(self.get_base_segment_list()) | set(self.get_domain_segment_list()))

    def get_macro_list(self) -> List[str]:
        return list(set(self.get_base_macro_list()) | set(self.get_domain_macro_list()))

    def is_segment_valid(self, segment_name: str) -> bool:
        return segment_name in self.get_segment_list()

    def is_macro_valid(self, macro_name: str) -> bool:
        return macro_name in self.get_macro_list()

    def get_file_path_from_segment_name(self, segment_name: str, version: str = str()):
        default_version: str = "99"
        paths: List[str] = [self.get_domain_path(), self.get_base_path()]
        versions: List[str] = [version] if version == default_version else [version, default_version]
        extensions: List[str] = [FileTag.ASSEMBLER, FileTag.LISTING]
        for path, file_version, extension in product(paths, versions, extensions):
            filename: str = f"{segment_name.lower()}{file_version}.{extension}"
            file_path: str = os.path.join(path, filename)
            if os.path.exists(file_path):
                return file_path
        raise SourceFileNotFound

    def get_file_path_from_macro_name(self, macro_name: str):
        paths: List[str] = [self.get_domain_path(), self.get_base_path()]
        for path in paths:
            filename: str = f"{macro_name.lower()}.{FileTag.MACRO}"
            file_path: str = os.path.join(path, filename)
            if os.path.exists(file_path):
                return file_path
        raise SourceFileNotFound

    def create_base_segment_list(self) -> List[str]:
        return FilePath(self.get_domain_path()).get_segment_list()

    def create_domain_segment_list(self) -> List[str]:
        return FilePath(self.get_domain_path()).get_segment_list()

    def create_domain_macro_list(self) -> List[str]:
        return FilePath(self.get_domain_path()).get_macro_list()

    def create_base_macro_list(self) -> List[str]:
        return FilePath(self.get_base_path()).get_macro_list()
