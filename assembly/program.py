import os
from typing import Dict

from assembly.macro import SegmentMacro, DataMacro
from assembly.segment import Segment
from config import config


class Program:
    ASM_EXT = {'.asm', '.txt'}
    ASM_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'asm')
    MAC_EXT = {'.mac', '.txt'}
    MAC_FOLDER_NAME = os.path.join(config.ROOT_DIR, 'macro')

    def __init__(self):
        self.segments: Dict[str, Segment] = dict()          # Dictionary of Segment. Segment name is the key.
        self.macros: Dict[str, DataMacro] = dict()
        for file_name in os.listdir(self.ASM_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.ASM_EXT:
                continue
            seg_name = file_name[:-4].upper()
            seg_macro = SegmentMacro(self, seg_name)
            self.segments[seg_name] = Segment(os.path.join(self.ASM_FOLDER_NAME, file_name), seg_name, seg_macro)
        for file_name in os.listdir(self.MAC_FOLDER_NAME):
            if len(file_name) < 6 or file_name[-4:].lower() not in self.MAC_EXT:
                continue
            macro_name = file_name[:-4].upper()
            self.macros[macro_name] = DataMacro(macro_name, os.path.join(self.MAC_FOLDER_NAME, file_name))
        self.macros['EB0EB'].load()
        self.macros['GLOBAL'].load()
        self.macros['WA0AA'].load()
        self.macros['MI0MI'].load()

    def __repr__(self):
        return f"Program:S={len(self.segments)}:M={len(self.macros)}"

    def load(self, seg_name):
        self.segments[seg_name].load()

    def is_macro_present(self, macro_name):
        return macro_name in self.macros


program = Program()
