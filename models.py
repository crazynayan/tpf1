from firestore_model import FirestoreModel


class Block(FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        self.to_blocks = list()
        self.function_calls = list()

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        block = f'{self.label} --> {self.to_blocks}'
        if self.function_calls:
            block += f', {self.label} -*> {self.function_calls}'
        return block

    def add_to_blocks(self, labels):
        for label in labels:
            if label not in self.to_blocks:
                self.to_blocks.append(label)


class Path(FirestoreModel):
    COLLECTION = 'path'
    DEFAULT = 'name'

    def __init__(self, name=None, asm_path=None):
        super().__init__()
        self.name = name if name else 'ERROR PROGRAM'
        self.path = asm_path if asm_path else list()







