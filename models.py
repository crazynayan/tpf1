from firestore_model import FirestoreModel


class Component:
    MAP_OBJECTS = {'reference'}
    TYPE = {
        'compare': {'CLC', 'CLI', 'LTR', 'TM'},
        'set': {'MVC', 'MVI', 'OI', 'NI'},
        'call': {'BAS', 'JAS', 'ENTRC'},
        'exit': {'B', 'J', 'ENTNC', 'ENTDC', 'BR', 'EXITC', 'SENDA'}
    }

    def __init__(self):
        self.type = None
        self.reference = Reference()
        self.command = None
        self.operands = list()
        self.output = None
        self.input = None

    def to_dict(self):
        block_dict = self.__dict__
        for key in self.MAP_OBJECTS:
            block_dict[key] = getattr(self, key).to_dict()
        return block_dict


class Reference:
    # For each element in LISTS add its initialization in the __init__ method
    LISTS = {'goes', 'calls', 'loops'}

    def __init__(self, ref=None, **kwargs):
        self.goes = list()
        self.calls = list()
        self.loops = list()
        self.add(ref, **kwargs)

    def add(self, ref=None, **kwargs):
        if ref and isinstance(ref, Reference):
            kwargs = ref.to_dict()
        for key in kwargs:
            if key in self.LISTS and kwargs[key]:
                if isinstance(kwargs[key], list):
                    for label in kwargs[key]:
                        if label not in getattr(self, key):
                            getattr(self, key).append(label)
                elif isinstance(kwargs[key], str) and kwargs[key] not in getattr(self, key):
                    getattr(self, key).append(kwargs[key])

    def to_dict(self):
        return self.__dict__


class Block(FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    MAP_OBJECTS = {'reference'}

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        # Pointers to other different type of blocks
        self.reference = Reference()
        self.depth = 0

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        block = [f'{self.label}({self.depth})']
        if self.reference.goes:
            block.append(f' --> {self.reference.goes}')
        if self.reference.calls:
            block.append(f' |-> {self.reference.calls}')
        if self.reference.loops:
            block.append(f' <-> {self.reference.loops}')
        return ''.join(block)

    def get_next(self):
        return self.reference.goes

    def get_calls(self):
        return self.reference.calls

    def get_loops(self):
        return self.reference.loops

    def to_dict(self):
        block_dict = super().to_dict()
        for key in self.MAP_OBJECTS:
            block_dict[key] = getattr(self, key).to_dict()
        return block_dict


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
