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
        self.align_to_boundary = 0
        self.start = -1
        self.end = -1

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
        boundary = DataType(dsdc.data_type).align_to_boundary
        if boundary > 0 and location_counter % boundary > 0:
            dsdc.align_to_boundary = boundary - location_counter % boundary
        # Length
        if operands[2]:
            dsdc.length = int(operands[2])
            dsdc.align_to_boundary = 0
        elif operands[3]:
            dsdc.length, result = macro.get_value(operands[3], location_counter)
            dsdc.align_to_boundary = 0
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
        # Start (after boundary alignment) and End (After duplication factor)
        dsdc.start = location_counter + dsdc.align_to_boundary
        dsdc.end = dsdc.start + dsdc.duplication_factor * dsdc.length
        return dsdc, Error.NO_ERROR


class Ds:
    @staticmethod
    def update(line, macro, location_counter, name, **_):
        operands = line.split_operands()
        dc, result = DsDc.from_operand(operands[0], macro, location_counter)
        if result != Error.NO_ERROR:
            return location_counter, result
        if line.label:
            macro.data_map[line.label] = SymbolTable(line.label, dc.start, dc.length, name)
        location_counter = dc.end
        if len(operands) > 1:
            for operand in operands[1:]:
                dc, result = DsDc.from_operand(operand, macro, location_counter)
                if result != Error.NO_ERROR:
                    return location_counter, result
                location_counter = dc.end
        return location_counter, Error.NO_ERROR


class Dc:
    @staticmethod
    def update(line, macro, location_counter, name, constant):
        operands = line.split_operands()
        dc, result = DsDc.from_operand(operands[0], macro, location_counter)
        if result != Error.NO_ERROR:
            return location_counter, result
        constant.start = constant.start or dc.start
        if line.label:
            macro.data_map[line.label] = SymbolTable(line.label, dc.start, dc.length, name)
        location_counter = dc.end
        constant.data.extend([0x00] * dc.align_to_boundary)
        constant.data.extend(dc.data * dc.duplication_factor)
        if len(operands) > 1:
            for operand in operands[1:]:
                dc, result = DsDc.from_operand(operand, macro, location_counter)
                if result != Error.NO_ERROR:
                    return location_counter, result
                location_counter = dc.end
                constant.data.extend([0x00] * dc.align_to_boundary)
                constant.data.extend(dc.data * dc.duplication_factor)
        return location_counter, Error.NO_ERROR


class Equ:
    @staticmethod
    def update(line, macro, location_counter, name, **_):
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
    @staticmethod
    def update(line, macro, location_counter, **_):
        name = line.label
        seg_location_counter, _ = macro.dsect if macro.dsect is not None else (location_counter, None)
        macro.dsect = seg_location_counter, name
        macro.data_map[name] = SymbolTable(name, 0, 0, name)
        return 0, Error.NO_ERROR


class Csect:
    @staticmethod
    def update(line, macro, location_counter, **_):
        dsect_location_counter, name = macro.dsect
        macro.dsect = None
        macro.data_map[line.label] = SymbolTable(line.label, location_counter, 0, name)
        return dsect_location_counter, Error.NO_ERROR


class Org:
    @staticmethod
    def update(line, macro, location_counter, **_):
        return macro.get_value(line.operand, location_counter)


class Pgmid:
    @staticmethod
    def update(**_):
        return 8, Error.NO_ERROR


class Push:
    @staticmethod
    def update(macro, location_counter, **_):
        macro.using_stack.append(macro.using.copy())
        return location_counter, Error.NO_ERROR


class Pop:
    @staticmethod
    def update(macro, location_counter, **_):
        macro.using = macro.using_stack.pop()
        return location_counter, Error.NO_ERROR


class Using:
    @staticmethod
    def update(line, macro, location_counter, name, **_):
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

    @classmethod
    def from_line(cls, line, **kwargs):
        assembler_directive_object = cls(line.command)
        kwargs['line'] = line
        return assembler_directive_object.update(**kwargs)
