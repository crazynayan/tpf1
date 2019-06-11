from firestore_model import FirestoreModel, MapToModelMixin, CollectionMixin


class Register:
    INVALID = '??'
    REG = {
        'R0': ['0', '00', 'R0', 'R00', 'RAC'],
        'R1': ['1', '01', 'R1', 'R01', 'RG1'],
        'R2': ['2', '02', 'R2', 'R02', 'RGA'],
        'R3': ['3', '03', 'R3', 'R03', 'RGB'],
        'R4': ['4', '04', 'R4', 'R04', 'RGC'],
        'R5': ['5', '05', 'R5', 'R05', 'RGD'],
        'R6': ['6', '06', 'R6', 'R06', 'RGE'],
        'R7': ['7', '07', 'R7', 'R07', 'RGF'],
        'R8': ['8', '08', 'R8', 'R08', 'RAP'],
        'R9': ['9', '09', 'R9', 'R09', 'REB'],
        'R10': ['10', 'R10', 'RLA'],
        'R11': ['10', 'R10', 'RLB'],
        'R12': ['10', 'R10', 'RLC'],
        'R13': ['10', 'R10', 'RLD'],
        'R14': ['10', 'R10', 'RDA'],
        'R15': ['10', 'R10', 'RDB'],
    }

    def __init__(self, reg):
        self.reg = next((key for key in self.REG for reg_val in self.REG[key] if reg_val == reg), None)

    def __repr__(self):
        return self.reg if self.reg else self.INVALID


class Operand(MapToModelMixin):
    pass


class Reference(MapToModelMixin):
    # For each element in TYPE add its initialization in the __init__ method
    TYPE = {'goes', 'calls', 'loops'}

    def __init__(self, ref_type=None, label=None):
        self.type = ref_type
        self.label = label

    def __repr__(self):
        return f'{self.type} to {self.label}' if self.type else self.INITIALIZE

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__repr__() == other
        elif isinstance(other, type(self)):
            return self.type == other.type and self.label == other.label


class References(CollectionMixin):
    MAP_OBJECTS = {Reference}

    def __init__(self, ref=None, **kwargs):
        super().__init__(Reference)
        self.add(ref, **kwargs)

    def add(self, ref=None, **kwargs):
        if ref and isinstance(ref, Reference):
            self.append_unique(ref)
            return
        if ref and isinstance(ref, References):
            self.extend_unique(ref)
            return
        for key in kwargs:
            if key in Reference.TYPE and kwargs[key]:
                new_ref = Reference(ref_type=key, label=kwargs[key])
                self.append_unique(new_ref)

    def get_next(self):
        return [ref.label for ref in self.list_values if ref.type == 'goes']

    def get_loops(self):
        return [ref.label for ref in self.list_values if ref.type == 'loops']

    def get_calls(self):
        return [ref.label for ref in self.list_values if ref.type == 'calls']


class Component(MapToModelMixin):
    MAP_OBJECTS = {Reference, Operand}
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
        # self.operand1 = Operand()
        # self.operand2 = Operand()
        self.operands = list()
        self.output = None
        self.input = None


class Block(MapToModelMixin, FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    MAP_OBJECTS = {References, Component}

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        self._references = References()
        self.component = Component()
        self.depth = 0

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        return f'{self.label}({self.depth})'

    def get_str(self):
        block = [self.__repr__()]
        if self.get_next():
            block.append(f' --> {self.get_next()}')
        if self.get_calls():
            block.append(f' |-> {self.get_calls()}')
        if self.get_loops():
            block.append(f' <-> {self.get_loops()}')
        return ''.join(block)

    def get_next(self):
        return self._references.get_next()

    def get_calls(self):
        return self._references.get_calls()

    def get_loops(self):
        return self._references.get_loops()

    def add_references(self, ref=None, **kwargs):
        self._references.add(ref, **kwargs)


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
