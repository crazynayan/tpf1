from copy import copy
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
        elif operand.count("'") == 2 and '-' not in operand:
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
            elif data_type == 'B':
                self.field = int(data_value, 2)
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
        elif '-' in operand:
            words = operand.split('-', 1)
            operand1 = Operand(words[0])
            operand2 = Operand(words[1])
            if operand1.constant and operand1.constant == 255 and operand2.variable:
                self.field = operand2.variable
                self.type.append(self.FLD)
            elif operand1.constant and operand2.constant:
                self.field = operand1.constant - operand2.constant
                self.type.append(self.CONSTANT)
            else:
                self.field = words[0]
                self.type.append(self.FLD)
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


class Operands(CollectionMixin):
    MAP_OBJECTS = {Operand}

    def __init__(self):
        super().__init__(Operand)


class Reference(CollectionItemMixin):
    TYPE = {'goes', 'calls', 'loops', 'falls', 'returns'}
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
                    # B, J (But not BR)
                    self.add_references(goes=line.operands[0])
            else:   # All other commands
                self.add_refs_with_key_value(labels)
        # Combine operands for bit instructions like TM, NI, OI
        operand1 = self.operands.list_values[0] if len(self.operands.list_values) > 0 else None
        operand2 = self.operands.list_values[1] if len(self.operands.list_values) > 1 else None
        if cmd.check(self.command, 'combine_operands'):
            if operand1.variable == 'WA0ET4' and operand2.constant == 0x10:
                operand2 = Operand('#WA0TTY')
            self.operands = Operands()
            self.operands.append(Operand.combine(operand1, operand2))
        # Combine operands if same
        if operand2 is not None and operand1 == operand2:
            self.operands.remove(operand2)
        # Update operand for BCTR
        if self.command == 'BCTR' and operand2.constant == 0:
            self.operands.remove(operand2)
            self.operands.append(Operand('1'))

    def __repr__(self):
        component = [f'{self.command}']
        for reference in self.references.list_values:
            component.append(f'->{reference}')
        return self.get_str(''.join(component))

    @property
    def is_exit(self):
        return cmd.check(self.command, 'exit')

    @property
    def is_program_exit(self):
        return cmd.check(self.command, 'exit') and \
               not cmd.check(self.command, 'has_branch') and \
               not cmd.check(self.command, 'return')

    @property
    def is_key_value(self):
        return True if [operand for operand in self.operands.list_values if operand.key_value] else False

    @property
    def is_conditional(self):
        return True if self.get_goes() and not cmd.check(self.command, 'has_branch') else False

    @property
    def is_set(self):
        return cmd.check(self.command, 'set_1') or cmd.check(self.command, 'set_2')

    @property
    def is_call(self):
        return cmd.check(self.command, 'call') and cmd.check(self.command, 'has_branch')

    @property
    def is_return(self):
        return cmd.check(self.command, 'return') and not self.operands.is_empty

    @property
    def fall_down(self):
        return next((ref.label for ref in self.references.list_values if ref.type == 'falls'), None)

    @property
    def condition(self):
        return next((ref.condition for ref in self.references.list_values if ref.type == 'goes'), None)

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

    def get_returns(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'returns']

    def get_goes(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'goes']

    def get_calls(self):
        return [ref.label for ref in self.references.list_values if ref.type == 'calls']

    def _get_conditional_text(self, direction=True, labels=None):
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

    def execute(self, state):
        state = state.copy()
        operand1 = self.operands.list_values[0]
        operand2 = self.operands.list_values[1] if len(self.operands.list_values) > 1 else None
        math = cmd.check(self.command, 'math')
        if self.is_set:
            set_text = self._get_set_text()
            pre_text = state.get_text(operand1, operand2)
            if operand2 is None:
                if operand1.bit:
                    if isinstance(operand1.bit['bits'], int):
                        _, target_value = state.get_type_value(operand1.bit['byte'])
                        source_value = eval(f"operand1.bit['bits'] {math} target_value")
                        state.assign_with_1(operand1.bit['byte'], source_value)
                    else:  # TODO remove the complication of bit being a string by doing macro lookup in operand create
                        source_value = 0 if math == '&' else 1
                        state.assign_with_1(operand1, source_value)
                else:
                    state.assign_with_1(operand1, 0)
            else:
                if cmd.check(self.command, 'set_2'):
                    operand1, operand2 = operand2, operand1
                state.assign_with_2(operand1, operand2, math)
            post_text = state.get_text(operand1, operand2)
            if state.capture_set:
                state.text.append(f'    {set_text:36}{pre_text:40}{post_text:40}{state.label}')
        if self.is_conditional:
            update = False
            next_label = state.path[state.path.index(state.label) + 1] \
                if state.path.index(state.label) + 1 < len(state.path) else None
            if next_label in self.get_goes():
                operator = cmd.get_operator(self.condition)
                condition_text = self._get_conditional_text(direction=True, labels=state.path)
            else:
                operator = cmd.get_operator(self.condition, opposite=True)
                update = any(label in state.path[state.path.index(next_label):]
                             for label in self.get_goes() if next_label)
                condition_text = self._get_conditional_text(direction=False, labels=state.path)
            star = ''
            if self.is_key_value:
                pre_text = ''
                post_text = ''
            else:
                pre_text = state.get_text(operand1, operand2)
                if operand2 is None or math:
                    if not state.condition_with_1(operand1, operator, update):
                        state.valid = False
                        star = '*'
                else:
                    if not state.condition_with_2(operand1, operand2, operator, update):
                        state.valid = False
                        star = '*'
                post_text = state.get_text(operand1, operand2)
            state.text.append(f'{condition_text:40}{pre_text:40}{post_text:40}{star}{state.label}')
        return state


class Components(CollectionMixin):
    MAP_OBJECTS = {Component}

    def __init__(self):
        super().__init__(Component)


class State:
    CONSTANT = 'data'
    KNOWN = 'known'
    UPDATED = 'updated'
    CONDITION = 'condition'
    INIT = 'init'

    def __init__(self, path, label=None):
        self.path = path
        self.label = path[0] if label is None else label
        self.known = dict()
        self.updated = dict()
        self.condition = dict()
        self.init = dict()
        self.valid = True
        self.text = list()
        self.capture_set = True

    def get_type_value(self, operand):
        if not isinstance(operand, str) and operand.constant is not None:
            return self.CONSTANT, operand.constant
        operand = str(operand)
        if operand in self.known:
            return self.KNOWN, self.known[operand]
        if operand in self.updated:
            return self.UPDATED, self.updated[operand]
        if operand in self.condition:
            return self.CONDITION, self.condition[operand]
        if operand in self.init:
            return self.INIT, self.init[operand]
        return self.INIT, 0

    def _del_operand(self, operand):
        if operand in self.known:
            del self.known[operand]
        elif operand in self.updated:
            del self.updated[operand]
        elif operand in self.condition:
            del self.condition[operand]
        elif operand in self.init:
            del self.init[operand]

    def _set_value(self, operand, operand_type, value):
        if not isinstance(operand, str) and operand.constant is not None:
            return
        operand = str(operand)
        self._del_operand(operand)
        if operand_type == self.KNOWN or operand_type == self.CONSTANT:
            self.known[operand] = value
        elif operand_type == self.UPDATED:
            self.updated[operand] = value
        elif operand_type == self.CONDITION:
            self.condition[operand] = value
        elif operand_type == self.INIT:
            self.init[operand] = value

    def assign_with_2(self, operand1, operand2, math=None):
        operand1_type, operand1_value = self.get_type_value(operand1)
        operand2_type, operand2_value = self.get_type_value(operand2)
        if math:
            operand1_value = int(operand1_value) if isinstance(operand2_value, int) else operand1_value
            operand2_value = int(operand2_value) if isinstance(operand1_value, int) else operand2_value
            value = eval(f'{operand1_value} {math} {operand2_value}')
        else:
            operand1_type = operand2_type if operand2_type != self.CONDITION else self.UPDATED
            value = operand2_value
        if operand1_type == self.CONDITION:
            operand1_type = self.UPDATED
        self._set_value(operand1, operand1_type, value)

    def assign_with_1(self, operand, value):
        self._del_operand(str(operand))
        self._set_value(operand, self.KNOWN, value)

    def condition_with_1(self, operand, operator, update):
        """
        Evaluate for single operand component.
        operand type INIT are upgraded to CONDITION
        :param operand: The operand of type Operand
        :param operator: The operator ('==0' or '!=0') is used to get the value for INIT type.
                         Pass the opposite operator for condition that falls down.
        :param update: update type is UPDATED if True else the update type is CONDITION
        :return: True, if the con
        """
        operand_type, operand_value = self.get_type_value(operand)
        if operand_type == self.INIT:
            update_type = self.INIT if update else self.CONDITION
            update_type = self.INIT if operator == '!= 0' else update_type
            if not eval(f'operand_value {operator}'):
                operand_value = self._operand_value_by_operator(operator)
            self._del_operand(str(operand))
            self._set_value(operand, update_type, operand_value)
            return True
        else:
            return eval(f'operand_value {operator}')

    def condition_with_2(self, operand1, operand2, operator, update):
        operand1_type, operand1_value = self.get_type_value(operand1)
        operand2_type, operand2_value = self.get_type_value(operand2)
        operand1_value = str(operand1_value) if isinstance(operand2_value, str) else operand1_value
        operand2_value = str(operand2_value) if isinstance(operand1_value, str) else operand2_value
        update_type = self.INIT if update else self.CONDITION
        update_type = self.INIT if operator == '!=' else update_type
        if operand1_type == self.INIT:
            if not eval(f'operand1_value {operator} operand2_value'):
                operand1_value = self._operand_value_by_operator(operator, operand2_value)
            self._del_operand(str(operand1))
            self._set_value(operand1, update_type, operand1_value)
            return True
        elif operand2_type == self.INIT:
            if not eval(f'operand1_value {operator} operand2_value'):
                operand2_value = self._operand_value_by_operator(operator, operand1_value)
            self._del_operand(str(operand2))
            self._set_value(operand2, update_type, operand2_value)
            return True
        else:
            return eval(f'operand1_value {operator} operand2_value')

    def get_text(self, operand1, operand2=None):
        operand1_type, operand1_value = self.get_type_value(operand1)
        if operand2 is None:
            return f'{operand1}({operand1_type[0]})={operand1_value}'
        else:
            operand2_type, operand2_value = self.get_type_value(operand2)
            return f'{operand1}({operand1_type[0]})={operand1_value}, {operand2}({operand2_type[0]})={operand2_value}'

    @staticmethod
    def _operand_value_by_operator(operator, data=None):
        if data is None:
            value_list = [0, 1, -1]
        else:
            if isinstance(data, int):
                value_list = [data, data + 1, data - 1]
            elif isinstance(data, str):
                data1 = chr(ord(data[0]) + 1) + data[1:]
                data2 = chr(ord(data[0]) - 1) + data[1:]
                value_list = [data, data1, data2]
            else:
                value_list = [data]
        for value in value_list:
            if data is None and eval(f'value {operator}'):
                return value
            if data is not None and eval(f'data {operator} value'):
                return value
        return None

    def copy(self):
        state = copy(self)
        state.known = self.known.copy()
        state.updated = self.updated.copy()
        state.condition = self.condition.copy()
        state.init = self.init.copy()
        return state


class Node(MapToModelMixin, FirestoreModel):
    COLLECTION = 'block'
    DEFAULT = 'label'
    MAP_OBJECTS = {Components}

    def __init__(self, label=None, name=None):
        super().__init__()
        self.label = label if label else 'LABEL_ERROR'
        self.doc_id = self.label
        self.name = name
        self.components = Components()

    def create(self):
        self.update(self.doc_id)

    def __repr__(self):
        return f'{self.label}'

    @property
    def fall_down(self):
        return self.components[-1].fall_down

    @property
    def is_program_exit(self):
        return self.components[-1].is_program_exit

    @property
    def is_exit(self):
        return self.components[-1].is_exit

    @property
    def is_return(self):
        return self.components[-1].is_return

    def get_call(self):
        return next(iter(self.components[-1].get_calls()), None)

    def get_next(self):
        return self.components[-1].get_next()

    def get_returns(self):
        return self.components[-1].get_returns()

    def set_fall_down(self, label):
        """
        Used for creating nodes
        :param label: the label to fall down
        :return:
        """
        if self.components.is_empty:
            self.components.append(Component('NOP'))
        self.components[-1].add_references(falls=label)

    def set_return(self, label):
        self.components[-1].add_references(returns=label)

    def set_loop(self, label):
        self.components[-1].add_references(loops=label)

    def get_str(self):
        """
        Used by main method.
        :return:
        """
        text = [f'{self.label:12}']
        text.extend([f'{component}, ' for component in self.components.list_values])
        return ''.join(text)[:-2]
