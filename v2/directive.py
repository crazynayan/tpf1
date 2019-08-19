import re

from v2.data_type import DataType, Register
from v2.errors import Error
from v2.file_line import SymbolTable


class DsDc:
    def __init__(self):
        self.duplication_factor = 1
        self.length = 0
        self.data_type = None
        self.data = None
        self.align_to_boundary = False

    def __repr__(self):
        return f'{self.duplication_factor}:{self.data_type}:{self.length}:{self.data}'

    @classmethod
    def from_operand(cls, operand, macro, location_counter):
        dsdc = cls()
        # (^\d*)([CXHFDBZPAY]D?)(?:L([\d]+))?(?:L[(]([^)]+)[)])?(?:[']([^']+)['])?(?:[(]([^)]+)[)])?
        operands = next(iter(re.findall(
            r"(^\d*)"                       # 0 Duplication Factor - A number. (Optional)
            r"([CXHFDBZPAY]D?)"             # 1 Data Type - Valid Single character Data type. (Note: FD is valid)
            r"(?:L([\d]+))?"                # 2 Length - L followed by a number. (Optional)
            r"(?:L[(]([^)]*)[)])?"          # 3 Length - L followed by a expression enclosed in paranthesis. (Optional)
            r"(?:[']([^']*)['])?"           # 4 Data - Enclosed in quotes. (Optional)
            r"(?:[(]([^)]*)[)])?",          # 5 Data - Enclosed in parenthesis. (Optional)
            operand)))
        # Duplication Factor
        dsdc.duplication_factor = int(operands[0]) if operands[0] else 1
        # Data Type
        dsdc.data_type = operands[1]
        # Align to boundary
        dsdc.align_to_boundary = DataType(dsdc.data_type).align_to_boundary
        # Length
        if operands[2]:
            dsdc.length = int(operands[2])
            dsdc.align_to_boundary = False
        elif operands[3]:
            dsdc.length, result = macro.get_value(operands[3], location_counter)
            dsdc.align_to_boundary = False
            if result != Error.NO_ERROR:
                return dsdc, result
        else:
            dsdc.length = None
        # Data
        if operands[4]:
            data_type_object = DataType(dsdc.data_type, input=operands[4])
            dsdc.length = dsdc.length or data_type_object.length
            dsdc.data = data_type_object.to_bytes(dsdc.length)
        elif operands[5]:
            number, result = macro.get_value(operands[5], location_counter)
            if result != Error.NO_ERROR:
                return dsdc, result
            data_type_object = DataType(dsdc.data_type, input=str(number))
            dsdc.length = dsdc.length or data_type_object.default_length
            dsdc.data = data_type_object.to_bytes(dsdc.length)
        else:
            dsdc.data = None
            dsdc.length = dsdc.length or DataType(dsdc.data_type).default_length
        return dsdc, Error.NO_ERROR


class Ds:
    @staticmethod
    def update(**kwargs):
        line = kwargs['line']
        macro = kwargs['macro']
        location_counter = kwargs['location_counter']
        name = kwargs['name']
        operands = line.split_operands()
        dsp = location_counter
        length = 0
        for operand in operands:
            dc, result = DsDc.from_operand(operand, macro, location_counter)
            if result != Error.NO_ERROR:
                return location_counter, result
            while dc.align_to_boundary and location_counter % DataType(dc.data_type).default_length != 0:
                dsp = dsp + 1 if operand == operands[0] else dsp
                location_counter += 1
            length = length or dc.length
            location_counter += dc.duplication_factor * dc.length
        if line.label:
            macro.data_map[line.label] = SymbolTable(line.label, dsp, length, name)
        return location_counter, Error.NO_ERROR


class Dc:
    @staticmethod
    def update(line, macro, location_counter, name, constant):
        operands = line.split_operands()
        dsp = location_counter
        length = 0
        for operand in operands:
            dc, result = DsDc.from_operand(operand, macro, location_counter)
            if result != Error.NO_ERROR:
                return location_counter, result
            while dc.align_to_boundary and location_counter % DataType(dc.data_type).default_length != 0:
                dsp = dsp + 1 if operand == operands[0] else dsp
                location_counter += 1
                constant.data.extend([0x00])
            constant.start = constant.start or location_counter
            length = length or dc.length
            location_counter += dc.duplication_factor * dc.length
            constant.data.extend(dc.data * dc.duplication_factor)
        if line.label:
            macro.data_map[line.label] = SymbolTable(line.label, dsp, length, name)
        return location_counter, Error.NO_ERROR


class Equ:
    # noinspection PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        if line.label is None:
            return location_counter, Error.EQU_LABEL_REQUIRED
        operands = line.split_operands()
        dsp_operand = operands[0]
        length = 1
        if dsp_operand == '*' or not set("+-*").intersection(dsp_operand):
            dsp, data_type, result = macro.evaluate(dsp_operand, location_counter)
            if result != Error.NO_ERROR:
                return location_counter, result
            if data_type == macro.FIELD_LOOKUP:
                dsp_operand = next(iter(dsp_operand.split('&')))
                length = macro.data_map[dsp_operand].length
        else:
            dsp, result = macro.get_value(dsp_operand, location_counter)
            if result != Error.NO_ERROR:
                return location_counter, result
        if len(operands) > 1:
            length, result = macro.get_value(operands[1])
            if result != Error.NO_ERROR:
                return location_counter, result
        macro.data_map[line.label] = SymbolTable(line.label, dsp, length, name)
        return location_counter, Error.NO_ERROR


class Dsect:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        name = line.label
        seg_location_counter, _ = macro.dsect if macro.dsect is not None else (location_counter, None)
        macro.dsect = seg_location_counter, name
        macro.data_map[name] = SymbolTable(name, 0, 0, name)
        return 0, Error.NO_ERROR


class Csect:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        dsect_location_counter, name = macro.dsect
        macro.dsect = None
        macro.data_map[line.label] = SymbolTable(line.label, location_counter, 0, name)
        return dsect_location_counter, Error.NO_ERROR


class Org:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name=None, constant=None):
        return macro.get_value(line.operand, location_counter)


class Pgmid:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        return 8, Error.NO_ERROR


class Push:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        macro.using_stack.append(macro.using.copy())
        return location_counter, Error.NO_ERROR


class Pop:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        macro.using = macro.using_stack.pop()
        return location_counter, Error.NO_ERROR


class Using:
    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def update(line, macro, location_counter, name, constant=None):
        operands = line.split_operands()
        if len(operands) == 2 and Register(operands[1]).is_valid():
            dsect = name if operands[0] == '*' else operands[0]
            macro.set_using(dsect, operands[1])
            return location_counter, Error.NO_ERROR
        else:
            raise TypeError


class AssemblerDirective:
    AD = {'DS': Ds, 'DC': Dc, 'EQU': Equ, 'DSECT': Dsect, 'CSECT': Csect, 'ORG': Org, 'PGMID': Pgmid,
          'PUSH': Push, 'POP': Pop, 'USING': Using}

    def __init__(self, ad_type):
        if ad_type not in self.AD:
            raise KeyError
        self.ad_type = ad_type

    def update(self, **kwargs):
        return self.AD[self.ad_type].update(**kwargs)

    def second_pass(self, ad_list, macro, name, errors):
        for line, location_counter in ad_list:
            if line.command != self.ad_type:
                continue
            _, result = self.AD[self.ad_type].update(line=line, macro=macro, location_counter=location_counter,
                                                     name=name)
            if result != Error.NO_ERROR:
                errors.append(f'{result} {line} {name}')
