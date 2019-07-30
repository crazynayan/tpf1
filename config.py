import os


class _Config:
    GAC_KEY_PATH = 'tpf1-key.json'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


config = _Config()
