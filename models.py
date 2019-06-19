from firestore_model import FirestoreModel, MapToModelMixin, CollectionMixin, CollectionItemMixin
from commands import cmd


class Register:
    INVALID = '??'
    REG = {
        'R0': ['R0', 'R00', 'RAC'],
        'R1': ['R1', 'R01', 'RG1'],
        'R2': ['R2', 'R02', 'RGA'],
        'R3': ['R3', 'R03', 'RGB'],
        'R4': ['R4', 'R04', 'RGC'],
        'R5': ['R5', 'R05', 'RGD'],
        'R6': ['R6', 'R06', 'RGE'],
        'R7': ['R7', 'R07', 'RGF'],
        'R8': ['R8', 'R08', 'RAP'],
        'R9': ['R9', 'R09', 'REB'],
        'R10': ['R10', 'RLA'],
        'R11': ['R11', 'RLB'],
        'R12': ['R12', 'RLC'],
        'R13': ['R13', 'RLD'],
        'R14': ['R14', 'RDA'],
        'R15': ['R15', 'RDB'],
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
        # BASE_DSP_LEN = 'bdl'
        # BASE_DSP_IDX = 'bdx'
        # FLD_LEN = 'fl'
        # FLD_DSP = 'fd'
        # FLD_DSP_LEN = 'fdl'
        # BASE_DSP_OTH = 'bdo'
        KEY_VALUE = 'kv'
        # ONLY_VALUE = 'v'
        CONSTANT = 'c'

    def __init__(self, operand=None):
        super().__init__()
        self.type = None
        self.field = None                   # Will be the field name or the complete operand text
        if operand:
            self.set(operand)

    def __repr__(self):
        text = self.field
        if self.type == self.OperandType.KEY_VALUE:
            text = f"{self.field['key']}:{self.field['value']}"
        elif self.type == self.OperandType.CONSTANT:
            text = str(self.field)
        elif self.type == self.OperandType.BASE_DSP:
            if 'length' in self.field:
                text = f"{self.field['base']}[{self.field['dsp']}:{self.field['dsp']+self.field['length']}]"
            else:
                text = f"{self.field['base']}[{self.field['dsp']}]"
        return self.get_str(text)

    def set(self, operand):
        """
        Parse the operand string and set the fields in Operand object appropriately
        :param operand: is a string of characters
        :return: None
        """
        if not operand:
            return
        if Register(operand).is_valid():
            self.type = self.OperandType.REG
            self.field = str(Register(operand))
        elif len(operand) > 1 and '=' in operand[1:]:
            # This is a key value operand.
            # Generally found in user defined macros (for e.g. FIELD=NAME)
            self.type = self.OperandType.KEY_VALUE
            key = operand.split('=')[0]
            value = operand.split('=')[1]
            self.field = {'key': key, 'value': value}
        elif operand.count("'") == 2:
            # This is a constant data.
            # Either an immediate or constant or literal data type where the values are present inline.
            self.type = self.OperandType.CONSTANT
            data_type = operand[1] if operand[0] == '=' else operand[0]
            data_type = data_type.upper()
            start_index = operand.find("'") + 1
            end_index = start_index + operand[start_index:].find("'")
            data_value = operand[start_index: end_index]
            if data_type == 'X':
                self.field = int(data_value, 16)
            elif data_type == 'C':
                self.field = data_value
            elif data_type == 'H' or data_type == 'F':
                self.field = int(data_value)
        elif operand[0].isdigit() and '(' not in operand:
            self.type = self.OperandType.CONSTANT
            self.field = int(operand)
        elif operand[0].isdigit() and '(' in operand:
            self.type = self.OperandType.BASE_DSP
            # Remove the trailing )
            operand = operand[:-1]
            words = operand.split('(')
            displacement = int(words[0])
            index = None
            length = None
            if ';' in operand:
                words = words[1].split(';')
                if Register(words[0]).is_valid() and Register(words[1]).is_valid():
                    index = str(Register(words[0]))
                    base = str(Register(words[1]))
                else:
                    if Register(words[0]).is_valid():
                        base = str(Register(words[0]))
                    else:
                        base = str(Register(words[1]))
                        length = int(words[0]) if words[0] else None
            else:
                base = str(Register(words[1]))
            self.field = {'base': base, 'dsp': displacement}
            if index:
                self.field['index'] = index
            if length:
                self.field['length'] = length
        else:
            self.type = self.OperandType.FLD
            self.field = operand

    @property
    def key_value(self):
        return self.field if self.type == self.OperandType.KEY_VALUE else None

    @property
    def base_dsp(self):
        return self.field if self.type == self.OperandType.BASE_DSP else None

    @property
    def variable(self):
        return self.field if self.type == self.OperandType.FLD else None

    @property
    def register(self):
        return self.field if self.type == self.OperandType.REG else None

    @property
    def constant(self):
        return self.field if self.type == self.OperandType.CONSTANT else None


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
                line = next((line for line in lines if cmd.check(line.command, 'check_cc')), None)
                if line and line.operands:
                    self.add_references(goes=line.operands[0], on=line.command)
        else:   # There is only one line
            line = lines[0]
            self.add_operands(line.operands)
            if cmd.check(line.command, 'has_branch'):
                # Instructions that have a branch label independent of the CC (BAS, B ...).
                if cmd.check(line.command, 'call') and len(line.operands) > 1:
                    # BAS, JAS
                    self.add_references(calls=line.operands[1])
                elif len(line.operands) > 0:
                    # B, J
                    self.add_references(goes=line.operands[0])
            else:   # All other commands
                self.add_refs_with_key_value(labels)
        if cmd.check(self.command, 'combine_operands'):
            self.combine_operands_for_tm()
        self.combine_operands_if_same()

    def combine_operands_for_tm(self):
        operand1 = self.operands[1]
        operand2 = self.operands[2]
        text = [f'{operand1}.']
        if operand2.variable:
            text.append(operand2.variable)
        else:  # Assume it to be of constant type
            # Identify bits
            bit_map = {'0': 0x80, '1': 0x40, '2': 0x20, '3': 0x10, '4': 0x08, '5': 0x04, '6': 0x02, '7': 0x01}
            bit_text = ['BIT']
            for bit, bit_value in bit_map.items():
                if operand2.constant & bit_value == bit_value:
                    bit_text.append(f'{bit}/')
            text.append(''.join(bit_text)[:-1])
            if text[0] == 'WA0ET4.' and text[1] == 'BIT3':
                text[1] = '#WA0TTY'
        self.operands = Operands()
        self.operands.append(Operand(''.join(text)))

    def combine_operands_if_same(self):
        if len(self.operands.list_values) != 2:
            return
        if self.operands[1] != self.operands[2]:
            return
        operand1 = self.operands[1]
        self.operands = Operands()
        self.operands.append(operand1)

    @property
    def is_exit(self):
        return cmd.check(self.command, 'exit')

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

    def get_goes(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'goes']

    def get_calls(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'calls']

    def get_text(self, direction=True, label=None):
        operands = self.operands.list_values
        if not operands:
            return ''
        is_key_value = [operand for operand in operands if operand.key_value]
        if is_key_value:
            cmd_text = self.command
            key = cmd.check(self.command, 'key_text')
            cmd_text2 = operands[0].variable if operands[0].variable else None
            cmd_text = f'{cmd_text}.{cmd_text2}' if cmd_text2 else cmd_text
            value = next((operand.key_value['value'] for operand in self.operands.list_values
                          if operand.key_value and operand.key_value['key'] == key), None)
            cmd_text = f'{cmd_text}.{value}' if value else cmd_text
            if direction:
                key = next((operand.key_value['key'] for operand in self.operands.list_values
                            if operand.key_value and operand.key_value['value'] == label), None)
                if not key:
                    return ''
                return f'{cmd_text} {key}'
            else:
                labels = self.get_goes()
                if not labels:
                    return ''
                keys = [operand.key_value['key'] for operand in self.operands.list_values
                        if operand.key_value and operand.key_value['value'] in labels]
                if not keys:
                    return ''
                keys_text = [f'{key[3:]} & ' if len(key) > 3 and key[:3] == 'NOT' else f'NOT {key} & ' for key in keys]
                keys_text = ''.join(keys_text)[:-3]
                return f'{cmd_text} {keys_text}'
        else:
            if cmd.check(self.command, 'has_branch'):
                return ''
            ref = next((ref for ref in self.references.list_values if ref.type == 'goes'), None)
            if not ref or not ref.label:
                return ''
            # TODO Do special processing for CLI commands to get the text 'is numeric' or 'is alphas'
            #  Weight 4972, 7832
            condition, operator = cmd.get_text(self.command, ref.condition, opposite=not direction)
            if len(operands) == 1:
                text = f'{operands[0]} {condition}'
            elif operator:
                text = f'{operands[0]} {operator} {operands[1]} {condition}'
            else:
                text = f'{operands[0]} {condition} {operands[1]}'
            return text


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

    def ends_in_program_exit(self):
        is_exit = self.ends_in_exit()
        if is_exit:
            is_exit = False if cmd.check(self.components[-1].command, 'has_branch') else True
        return is_exit

    def get_text(self, label, prefix=''):
        text_list = list()
        for component in self.components.list_values:
            text = None
            if label in component.get_goes():
                text = component.get_text(True, label)
                if text:
                    text_list.append(prefix + text)
                break
            elif component.get_goes():
                text = component.get_text(False)
            if text:
                text_list.append(prefix + text)
        if not text_list:
            return ''
        text_list.append('')
        return '\n'.join(text_list)

    def get_path(self, label):
        component_path = list()
        label_components = [c for c in self.components.list_values if label in c.get_next()]
        for label_component in label_components:
            components = dict()
            components[label] = list()
            for component in self.components.list_values:
                components[label].append(component)
                if component == label_component:
                    break
            component_path.append(components)
        return component_path


class Path(FirestoreModel):
    COLLECTION = 'path'
    DEFAULT = 'name'

    def __init__(self, name=None, asm_path=None):
        super().__init__()
        self.name = name if name else 'ERROR PROGRAM'
        self.path = asm_path if asm_path else list()
        self.weight = 0
        self.head = self.path[0] if self.path else None
        self.tail = self.path[-1] if self.path else None
        self.exit_on_loop = False
        self.exit_on_program = False

    def __repr__(self):
        return f'{self.name}-{self.head}({self.weight}, {len(self.path)})'
