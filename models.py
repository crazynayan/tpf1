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
    # Operand types
    REG = 'r'
    FLD = 'f'
    BASE_DSP = 'bd'
    KEY_VALUE = 'kv'
    CONSTANT = 'c'
    BIT = 'b'

    def __init__(self, operand=None):
        super().__init__()
        self.type = list()
        self.field = None                   # Will be the field name or the complete operand text
        if operand:
            self.set(operand)

    def __repr__(self):
        text = self.field
        if self.KEY_VALUE in self.type:
            text = f"{self.field['key']}:{self.field['value']}"
        elif self.BIT in self.type:
            if self.CONSTANT in self.type:
                bit_map = {'0': 0x80, '1': 0x40, '2': 0x20, '3': 0x10, '4': 0x08, '5': 0x04, '6': 0x02, '7': 0x01}
                bit_text = ['BIT']
                for bit, bit_value in bit_map.items():
                    if self.field['bits'] & bit_value == bit_value:
                        bit_text.append(f'{bit}/')
                bit_text = ''.join(bit_text)[:-1]
            else:
                bit_text = self.field['bits']
            if self.BASE_DSP in self.type:
                byte_text = f"{self.field['byte']['base']}[{self.field['byte']['dsp']}]"
            else:
                byte_text = self.field['byte']
            text = f"{byte_text}.{bit_text}"
        elif self.CONSTANT in self.type:
            text = str(self.field)
        elif self.BASE_DSP in self.type:
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
        if Register(operand).is_valid():
            self.type.append(self.REG)
            self.field = str(Register(operand))
        elif len(operand) > 1 and '=' in operand[1:]:
            # This is a key value operand.
            # Generally found in user defined macros (for e.g. FIELD=NAME)
            self.type.append(self.KEY_VALUE)
            key = operand.split('=')[0]
            value = operand.split('=')[1]
            if value[0] == "'":
                # For quoted text, replace ; with space and remove the quotes
                value = value.replace(';', ' ')
                value = value.replace("'", '')
            self.field = {'key': key, 'value': value}
        elif operand.count("'") == 2:
            # This is a constant data.
            # Either an immediate or constant or literal data type where the values are present inline.
            self.type.append(self.CONSTANT)
            data_type = operand[1] if operand[0] == '=' else operand[0]
            data_type = data_type.upper()
            data_type = operand[3] if data_type == 'A' or data_type == 'Y' else data_type
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
            self.type.append(self.CONSTANT)
            self.field = int(operand)
        elif operand[0].isdigit() and '(' in operand:
            self.type.append(self.BASE_DSP)
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
            self.type.append(self.FLD)
            # TODO Ignore Field with base/length/displacement for now
            self.field = operand.split('(', 1)[0].split('+', 1)[0].split('-', 1)[0]

    @property
    def key_value(self):
        return self.field if self.KEY_VALUE in self.type else None

    @property
    def base_dsp(self):
        return self.field if self.BASE_DSP in self.type and self.BIT not in self.type else None

    @property
    def variable(self):
        return self.field if self.FLD in self.type else None

    @property
    def register(self):
        return self.field if self.REG in self.type else None

    @property
    def constant(self):
        return self.field if self.CONSTANT in self.type and self.BIT not in self.type else None

    @property
    def bit(self):
        return self.field if self.BIT in self.type else None

    @classmethod
    def combine(cls, operand1, operand2):
        """
        Combine 2 operands for bit instructions into one operand.
        This can be called only after the 2 operands are created
        :param operand1: First operand (A field or a base-dsp)
        :param operand2: Second operand (A field or a bit value)
        :return: composite operand
        """
        model = cls()
        model.type.append(cls.BIT)
        model.type.extend([op_type for op_type in operand1.type])
        model.type.extend([op_type for op_type in operand2.type])
        model.field = dict()
        model.field['byte'] = operand1.field
        model.field['bits'] = operand2.field
        return model

    def get_any_reg(self):
        if self.register:
            return self.field
        elif self.base_dsp:
            return self.field['base']
        elif self.bit:
            return self.field['byte']['base'] if self.BASE_DSP in self.type else None
        else:
            return None

    def get_any_field(self):
        if self.bit:
            return self.field['byte']
        elif self.variable:
            return self.field
        return None

    def old_check(self, operands):
        """
        Check whether the current operand matches with any of the list in operands
        :param operands: A list of operands of type Operand
        :return: True if match is found else False
        """
        if self.key_value:
            return False
        elif self.register or self.base_dsp:
            register = self.field['base'] if self.base_dsp else self.field
            return register in [operand.get_any_reg() for operand in operands if operand.get_any_reg()]
        elif self.bit:
            if self.BASE_DSP in self.type:
                return self.field['byte']['base'] in [operand.get_any_reg()
                                                      for operand in operands if operand.get_any_reg()]
            else:
                return self.field['byte'] in [operand.get_any_field()
                                              for operand in operands if operand.get_any_field()]
        else:
            return self.field in [operand.get_any_field() for operand in operands if operand.get_any_field()]

    def check(self, operands):
        register = self.get_any_reg()
        field = self.get_any_field()
        for index, operand in enumerate(operands):
            if register and register == operand.get_any_reg():
                del operands[index]
                return True, operands
            if field and field == operand.get_any_field():
                del operands[index]
                return True, operands
        return False, operands


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
        self.references = References()
        self.command = None
        self.operands = Operands()
        # Set appropriate values
        if not lines:
            return
        if isinstance(lines, str):
            # Create dummy component
            self.command = lines
            return
        self.command = lines[0].command
        if cmd.check(self.command, 'no_operand'):
            return
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
        # Combine operands for bit instructions like TM, NI, OI
        if cmd.check(self.command, 'combine_operands'):
            operand1 = self.operands[1]
            operand2 = self.operands[2]
            if operand1.variable == 'WA0ET4' and operand2.constant == 0x10:
                operand2 = Operand('#WA0TTY')
            self.operands = Operands()
            self.operands.append(Operand.combine(operand1, operand2))
        # Combine operands if same
        if len(self.operands.list_values) == 2 and self.operands[1] == self.operands[2]:
            operand1 = self.operands[1]
            self.operands = Operands()
            self.operands.append(operand1)

    def __repr__(self):
        component = [f'{self.command}']
        for reference in self.references.list_values:
            component.append(f'->{reference}')
        return self.get_str(''.join(component))

    @property
    def is_exit(self):
        return cmd.check(self.command, 'exit')

    @property
    def is_key_value(self):
        return True if [operand for operand in self.operands.list_values if operand.key_value] else False

    @property
    def is_conditional(self):
        return True if self.get_goes() and not cmd.check(self.command, 'has_branch') else False

    @property
    def fall_down(self):
        return next((ref.label for ref in self.references.list_values if ref.type == 'falls'), None)

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

    def get_text(self, direction=True, labels=None):
        if not self.is_conditional:
            return self._get_set_text()
        operands = self.operands.list_values
        if not operands:
            return ''
        if self.is_key_value:
            cmd_text = self.command
            key = cmd.check(self.command, 'key_text')
            cmd_text2 = operands[0].variable if operands[0].variable else None
            cmd_text = f'{cmd_text}.{cmd_text2}' if cmd_text2 else cmd_text
            value = next((operand.key_value['value'] for operand in self.operands.list_values
                          if operand.key_value and operand.key_value['key'] == key), None)
            cmd_text = f'{cmd_text}.{value}' if value else cmd_text
            if direction:
                keys = [operand.key_value['key'] for operand in self.operands.list_values
                        if operand.key_value and operand.key_value['value'] in labels]
                if not keys:
                    return ''
                keys_text = ''.join([f'{key} or ' for key in keys])[:-3]
                return f'{cmd_text} {keys_text}'
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
            condition, operator = cmd.get_text(self.command, ref.condition, opposite=not direction)
            if len(operands) == 1:
                text = f'{operands[0]} {condition}'
            elif operator:
                text = f'{operands[0]} {operator} {operands[1]} {condition}'
            else:
                text = f'{operands[0]} {condition} {operands[1]}'
            return text

    def check_set(self, operands):
        if not cmd.check(self.command, 'set_1') and not cmd.check(self.command, 'set_2'):
            return False, operands
        if not self.operands.list_values:
            return False, operands
        operand1 = self.operands.list_values[0]
        operand2 = self.operands.list_values[1] if len(self.operands.list_values) > 1 else None
        if cmd.check(self.command, 'set_1'):
            found, remaining_operands = operand1.check(operands)
            if found:
                if operand2 and operand2.constant is None:
                    remaining_operands.append(operand2)
                if cmd.check(self.command, 'math'):
                    remaining_operands.append(operand1)
                return True, remaining_operands
        elif cmd.check(self.command, 'set_2') and operand2:
            found, remaining_operands = operand2.check(operands)
            if found:
                remaining_operands.append(operand1)
                return True, remaining_operands
        return False, operands

    def _get_set_text(self):
        if not self.operands.list_values:
            return ''
        operand1 = self.operands.list_values[0]
        operand2 = self.operands.list_values[1] if len(self.operands.list_values) > 1 else None
        if self.command == 'OI':
            return f'Turn ON {operand1}'
        elif self.command == 'NI':
            return f'Turn OFF {operand1}'
        elif not operand2:
            return f'{operand1} = 0'
        elif cmd.check(self.command, 'math'):
            return f"{operand1} {cmd.check(self.command, 'math')}= {operand2}"
        elif cmd.check(self.command, 'set_2'):
            return f'{operand2} = {operand1}'
        else:
            return f'{operand1} = {operand2}'


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

    @property
    def fall_down(self):
        return self.components[-1].fall_down if self.components.list_values else None

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

    def get_path(self, label):
        component_path = list()
        label_components = [c for c in self.components.list_values if label in c.get_next()]
        for label_component in label_components:
            components = dict()
            components['label'] = self.label
            components['items'] = list()
            for component in self.components.list_values:
                components['items'].append(component)
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
        self.exit_on_merge = False

    def __repr__(self):
        return f'{self.name}-{self.head}({self.weight}, {len(self.path)})'
