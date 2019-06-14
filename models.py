from firestore_model import FirestoreModel, MapToModelMixin, CollectionMixin, CollectionItemMixin
from commands import commands


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
            self.field = {'key': key, 'value': value}
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
    TYPE = {'goes', 'calls', 'loops', 'falls'}
    DEFAULT = 'type'

    def __init__(self, ref_type=None, label=None, condition=None):
        super().__init__()
        self.type = ref_type
        self.label = label
        self.condition = condition

    def __repr__(self):
        if self.condition:
            return self.get_str(f'{self.type} to {self.label} on {self.condition}')
        else:
            return self.get_str(f'{self.type} to {self.label}')


class References(CollectionMixin):
    MAP_OBJECTS = {Reference}

    def __init__(self):
        super().__init__(Reference)


class Component(CollectionItemMixin):
    MAP_OBJECTS = {References, Operands}
    DEFAULT = 'command'

    def __init__(self, lines=None, labels=None):
        super().__init__()
        self.type = None
        self.references = References()
        self.command = None
        self.operands = Operands()
        self.output = None
        self.input = None
        # Set appropriate values
        if not lines:
            return
        if isinstance(lines, str):
            # Create dummy component
            self.command = lines
            return
        self.command = lines[0].command
        if len(lines) > 1:
            if lines[0].continuation:
                # Continuing lines, generally executable macros withs key-value pairs.
                # TODO Does NOT take care of scenario of a single operand divided into multi-line
                for line in lines:
                    self.add_operands(line.operands)
                self.add_refs_with_key_value(labels)
            else:   # Multi-line with SET_CC and CHECK_CC
                # TODO Does NOT take care of scenario where there are lines between SET_CC and CHECK_CC
                self.add_operands(lines[0].operands)
                line = next((line for line in lines if commands[line.command]['check_cc']), None)
                if line and line.operands:
                    self.add_references(goes=line.operands[0], on=line.command)
        else:   # There is only one line
            line = lines[0]
            self.add_operands(line.operands)
            if commands[line.command]['has_branch']:
                # Instructions that have a branch label independent of the CC (BAS, B ...).
                if commands[line.command]['call'] and len(line.operands) > 1:
                    # BAS, JAS
                    self.add_references(calls=line.operands[1])
                elif len(line.operands) > 0:
                    # B, J
                    self.add_references(goes=line.operands[0])
            else:   # All other commands
                self.add_refs_with_key_value(labels)

    @property
    def is_exit(self):
        return commands[self.command]['exit']

    def __repr__(self):
        component = [f'{self.command}']
        for reference in self.references.list_values:
            component.append(f'->{reference}')
        return self.get_str(''.join(component))

    def add_operands(self, operands):
        for operand in operands:
            if operand:
                self.operands.append(Operand(operand))

    def add_references(self, **kwargs):
        on = kwargs['on'] if 'on' in kwargs else None
        for key in kwargs:
            if key in Reference.TYPE and kwargs[key]:
                new_ref = Reference(ref_type=key, label=kwargs[key], condition=on)
                self.references.append_unique(new_ref)

    def add_refs_with_key_value(self, labels):
        operands = [operand.key_value for operand in self.operands.list_values if operand.key_value]
        for operand in operands:
            if operand['value'] in labels:
                self.add_references(goes=operand['value'], on=operand['key'])

    def add_loop_ref(self, label):
        self.add_references(loops=label)

    def add_fall_down_ref(self, label):
        self.add_references(falls=label)

    def get_next(self):
        return [ref.label for ref in self.references.list_values if ref.type in {'goes', 'falls'}]

    def get_loops(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'loops']

    def get_calls(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'calls']


class Components(CollectionMixin):
    MAP_OBJECTS = {Component}

    def __init__(self):
        super().__init__(Component)


class Block(MapToModelMixin, FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    MAP_OBJECTS = {Components}

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
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
        labels = list()
        for component in self.components.list_values:
            for label in component.get_next():
                if label not in labels:
                    labels.append(label)
        return labels

    def get_calls(self):
        labels = list()
        for component in self.components.list_values:
            for label in component.get_calls():
                if label not in labels:
                    labels.append(label)
        return labels

    def get_loops(self):
        labels = list()
        for component in self.components.list_values:
            for label in component.get_loops():
                if label not in labels:
                    labels.append(label)
        return labels

    def set_fall_down(self, label):
        if self.components.is_empty:
            self.components.append(Component('NOP'))
        self.components[-1].add_fall_down_ref(label)  # TODO soft code NOP and fall_down later

    def add_loop_label(self, label):
        if self.components.is_empty:
            return
        components = [c for c in self.components.list_values for next_label in c.get_next() if next_label == label]
        for component in components:
            component.add_loop_ref(label)

    def ends_in_exit(self):
        if self.components.is_empty:
            return False
        return self.components[-1].is_exit


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
