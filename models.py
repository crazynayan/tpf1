from firestore_model import FirestoreModel


class Block(FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    GOES = 'goes'
    CALLS = 'calls'
    LOOPS = 'loops'

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        # Pointers to other different type of blocks
        self.reference = {
            self.GOES: list(),
            self.CALLS: list(),
            self.LOOPS: list(),
        }
        self.depth = 0

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        block = [f'{self.label}({self.depth})']
        if self.reference[self.GOES]:
            block.append(f' --> {self.reference[self.GOES]}')
        if self.reference[self.CALLS]:
            block.append(f' |-> {self.reference[self.CALLS]}')
        if self.reference[self.LOOPS]:
            block.append(f' <-> {self.reference[self.LOOPS]}')
        return ''.join(block)

    def add_references(self, labels):
        """
        Update the next references / pointers (goes, calls, loops) of the blocks.
        :param labels:  dictionary of self.reference
        :return: None
        """
        for key in labels:
            if key in self.reference:
                for label in labels[key]:
                    if label not in self.reference[key]:
                        self.reference[key].append(label)

    def get_next(self):
        return self.reference[self.GOES]

    def get_calls(self):
        return self.reference[self.CALLS]

    def get_loops(self):
        return self.reference[self.LOOPS]


class Path(FirestoreModel):
    COLLECTION = 'path'
    DEFAULT = 'name'

    def __init__(self, name=None, asm_path=None):
        super().__init__()
        self.name = name if name else 'ERROR PROGRAM'
        self.path = asm_path if asm_path else list()
        self.weight = 0
        self.head = self.path[0] if self.path else None

    def __repr__(self):
        return f'{self.name}-{self.head}({self.weight}, {len(self.path)})'
