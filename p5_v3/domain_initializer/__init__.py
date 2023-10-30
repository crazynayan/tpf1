import os
from importlib import import_module
from typing import Type

from munch import Munch

from p5_v3.p05_domain import ClientDomainCollection, ClientDomain


def initialize_domain(client_name: str, domain_name: str, user_defined_operation_code_format: Type[object]):
    ClientDomainCollection.CLIENTS[client_name.upper()] = client_name
    ClientDomainCollection.DOMAINS[domain_name.upper()] = domain_name
    if client_name not in ClientDomainCollection.CLIENT_DOMAIN:
        ClientDomainCollection.CLIENT_DOMAIN[client_name] = Munch()
    if domain_name not in ClientDomainCollection.CLIENT_DOMAIN[client_name]:
        ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name] = Munch()
    ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name][
        ClientDomainCollection.USER_DEFINED_OPERATION_CODE_CLASS_TAG] = user_defined_operation_code_format
    client_domain: ClientDomain = ClientDomain(client_name, domain_name)
    ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name][
        ClientDomainCollection.BASE_SEGMENT_LIST_TAG] = client_domain.create_base_segment_list()
    ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name][
        ClientDomainCollection.BASE_MACRO_LIST_TAG] = client_domain.create_base_macro_list()
    ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name][
        ClientDomainCollection.DOMAIN_SEGMENT_LIST_TAG] = client_domain.create_domain_segment_list()
    ClientDomainCollection.CLIENT_DOMAIN[client_name][domain_name][
        ClientDomainCollection.DOMAIN_MACRO_LIST_TAG] = client_domain.create_domain_macro_list()
    return


def initialize_all_domains():
    root_folder_name = "p5_v3"
    domain_initializer_folder_name = "domain_initializer"
    domain_initialize_path = os.path.join(root_folder_name, domain_initializer_folder_name)
    if not os.path.isdir(domain_initialize_path):
        raise Exception("Domain_Initializer path not initialized.")
    for filename in os.listdir(domain_initialize_path):
        if filename.startswith("_"):
            continue
        module_name = f"{root_folder_name}.{domain_initializer_folder_name}.{filename[:-3]}"
        module = import_module(module_name)
        initialize_domain(module.CLIENT_NAME, module.DOMAIN_NAME, module.UserDefinedOperationCodeFormat)
    return
