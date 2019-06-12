from firestore_model import FirestoreModel, MapToModelMixin, CollectionMixin, CollectionItemMixin


class Register:
    INVALID = '??'
    DEFAULT = '_reg'
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

    def __init__(self, reg=None):
        super().__init__()
        self._reg = next((key for key in self.REG for reg_val in self.REG[key] if reg_val == reg), self.INVALID)

    def __repr__(self):
        return self._reg

    def __set__(self, instance, value):
        self._reg = next((key for key in self.REG for reg_val in self.REG[key] if reg_val == value), self.INVALID)

    def __get__(self, instance, owner):
        return self._reg

    def is_valid(self):
        return self._reg != self.INVALID


class Operand(CollectionItemMixin):
    DEFAULT = 'type'

    class OperandType:
        REG = 'r'
        FLD = 'f'
        BASE_DSP = 'bd'
        BASE_DSP_LEN = 'bdl'
        BASE_DSP_IDX = 'bdx'
        FLD_LEN = 'fl'
        FLD_DSP = 'fd'
        FLD_DSP_LEN = 'fdl'
        BASE_DSP_OTH = 'bdo'
        IMMEDIATE = 'i'
        KEY_VALUE = 'kv'
        ONLY_VALUE = 'v'
        TYPE = (REG, FLD, BASE_DSP, BASE_DSP_LEN, BASE_DSP_IDX, FLD_LEN, FLD_DSP, FLD_DSP_LEN, BASE_DSP_OTH,
                IMMEDIATE, KEY_VALUE, ONLY_VALUE)

        def __init__(self, value=None):
            if not value:
                value = self.FLD
            if value not in self.TYPE:
                value = self.FLD
            self._type = value

        def __repr__(self):
            return self._type

        def __get__(self, instance, owner):
            return self._type

        def __set__(self, instance, value):
            if value not in self.TYPE:
                value = self.FLD
            self._type = value

    def __init__(self, operand=None):
        super().__init__()
        self.type = None
        self.field = None                   # Will be the field name or the complete operand text
        self.constant = False               # For literals it will be True. TODO change it to Constant()
        if operand:
            self.set(operand)

    def __repr__(self):
        return self.get_str(f'{self.field}({self.type})')

    def set(self, operand):
        """
        Parse the operand string and set the fields in Operand object appropriately
        :param operand: is a string of characters
        :return: None
        """
        if Register(operand).is_valid():
            self.type = self.OperandType.REG
            self.field = str(Register(operand))
        elif len(operand) > 1 and '=' in operand[1:]:
            self.type = self.OperandType.KEY_VALUE
            key = operand.split('=')[0]
            value = operand.split('=')[1]
            self.field = (key, value)
        else:
            self.type = self.OperandType.FLD
            self.field = operand

    @property
    def key_value(self):
        return self.field if self.type == self.OperandType.KEY_VALUE else None


class Operands(CollectionMixin):
    MAP_OBJECTS = {Operand}

    def __init__(self):
        super().__init__(Operand)


class Reference(CollectionItemMixin):
    TYPE = {'goes', 'calls', 'loops'}
    DEFAULT = 'type'

    def __init__(self, ref_type=None, label=None):
        super().__init__()
        self.type = ref_type
        self.label = label

    def __repr__(self):
        return self.get_str(f'{self.type} to {self.label}')


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


class Component(CollectionItemMixin):
    MAP_OBJECTS = {References, Operands}
    DEFAULT = 'type'
    CONTINUED = 'CONTINUED'
    BRANCH = {'B', 'BE', 'BNE', 'BH', 'BNH', 'BL', 'BNL', 'BM', 'BNM', 'BP', 'BNP', 'BC', 'BO', 'BNO', 'BZ', 'BNZ',
              'J', 'JE', 'JNE', 'JH', 'JNH', 'JL', 'JNL', 'JM', 'JNM', 'JP', 'JNP', 'JC', 'JO', 'JNO', 'JZ', 'JNZ'}

    class ComponentType:
        COMPARE = 'compare'
        SET = 'set'
        CALL = 'call'
        EXIT = 'exit'
        OTHER = 'other'
        DATABASE = 'db'
        TYPES = [  # TODO Add SR in COMPARE and support multi-line compare which is optional
            {'type': COMPARE, 'command': {'CLC', 'CLI', 'LTR', 'TM', 'OC', 'CH'}, 'has_refs': True},
            {'type': SET, 'command': {'MVC', 'MVI', 'OI', 'NI', 'L', 'LA'}, 'has_refs': False},
            {'type': CALL, 'command': {'BAS', 'JAS', 'ENTRC'}, 'has_refs': False},
            {'type': EXIT, 'command': {'B', 'J', 'ENTNC', 'ENTDC', 'BR', 'EXITC', 'SENDA'}, 'has_refs': False},
            {'type': DATABASE, 'command': {'PDRED', 'DBRED'}, 'has_refs': True},
        ]

        def __init__(self, command=None, type=None):
            self.type = None
            if command:
                self.type = next((c_type for c_type in self.TYPES if command in c_type['command']), None)
            if type and not self.type:
                self.type = next((c_type for c_type in self.TYPES if type == c_type['type']), None)

        def get_type(self):
            return self.type['type'] if self.type else self.OTHER

        def has_refs(self):
            return self.type['has_refs'] if self.type else False

    def __init__(self, command=None, operands=None):
        super().__init__()
        self.type = None
        self.references = References()
        self.command = None
        self.operands = Operands()
        self.output = None
        self.input = None
        self.comparator = None
        self.set(command, operands)

    def set(self, command, operands):
        self.command = command
        self.type = self.ComponentType(command=self.command).get_type()
        self.add_operands(operands)
        if self.type == self.ComponentType.SET:
            self.output = Operands().append(self.operands[1])
            self.input = Operands().append(self.operands[2])
        elif self.type == self.ComponentType.COMPARE:
            self.input = self.operands

    def add_operands(self, operands):
        if isinstance(operands, Operands):
            self.operands.extend(operands)
        elif isinstance(operands, list) and operands:
            if isinstance(operands[0], str):
                for operand in operands:
                    if operand:
                        self.operands.append(Operand(operand))
            elif isinstance(operands[0], Operand):
                self.operands.extend(operands)

    def add_references(self, labels, command=None, operands=None):
        if command == self.CONTINUED:
            self.add_operands(operands)
            kv_list = [operand.key_value for operand in self.operands.list_values if operand.key_value]
            for kv in kv_list:
                if kv[1] in labels:
                    self.references.add(goes=kv[1])
                    self.comparator = kv[0]
            return
        if command in self.BRANCH or self.command in self.BRANCH:
            label = None
            if operands:
                label = next((label for label in operands if label in labels), None)
            if not label:
                label = next((operand.field for operand in self.operands.list_values if operand.field in labels), None)
            if label:
                self.references.add(goes=label)
                self.comparator = command
        if self.type == self.ComponentType.CALL:
            label = next((operand.field for operand in self.operands.list_values if operand.field in labels), None)
            if label:
                self.references.add(calls=label)

    def __repr__(self):
        component = [f'{self.command}']
        if self.type != self.ComponentType.OTHER:
            component.append(f' ({self.type})')
        if self.has_refs:
            component.append(f' {self.comparator}->{self.references[1]}')
        return self.get_str(''.join(component))

    @property
    def can_have_refs(self):
        return self.ComponentType(type=self.type).has_refs()

    @property
    def has_refs(self):
        return not self.references.is_empty


class Components(CollectionMixin):
    MAP_OBJECTS = {Component}

    def __init__(self):
        super().__init__(Component)


class Block(MapToModelMixin, FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    MAP_OBJECTS = {References, Components}

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        # TODO Make references methods in Block as property
        self.references = References()
        self.components = Components()
        self.depth = 0

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        return f'{self.label}({self.depth})'

    def get_str(self):
        block = [self.__repr__()]
        if not self.components.is_empty:
            block.append('\n')
            block.append(''.join([f'{comp}, ' for comp in self.components.list_values])[:-2])
            block.append('\n')
        if self.get_next():
            block.append(f' --> {self.get_next()}')
        if self.get_calls():
            block.append(f' |-> {self.get_calls()}')
        if self.get_loops():
            block.append(f' <-> {self.get_loops()}')
        return ''.join(block)

    def get_next(self):
        return self.references.get_next()

    def get_calls(self):
        return self.references.get_calls()

    def get_loops(self):
        return self.references.get_loops()

    def add_references(self, ref=None, **kwargs):
        self.references.add(ref, **kwargs)


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
