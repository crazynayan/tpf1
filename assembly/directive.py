import re
from typing import Dict, List, Tuple

from assembly2.mac0_generic import LabelReference
from assembly2.seg2_operand import Label
from config import config
from utils.data_type import DataType, Register
from utils.errors import Error
from utils.file_line import Line


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
    def from_operand(cls, operand, macro):
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
        if boundary > 0 and macro.location_counter % boundary > 0:
            dsdc.align_to_boundary = boundary - macro.location_counter % boundary
        # Length
        if operands[2]:
            dsdc.length = int(operands[2])
            dsdc.align_to_boundary = 0
        elif operands[3]:
            dsdc.length, result = macro.get_value(operands[3])
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
            dsdc.data = bytearray()
            for operand in operands[5].split(','):
                number, result = macro.get_value(operand)
                if result != Error.NO_ERROR:
                    return dsdc, result
                data_type_object = DataType(dsdc.data_type, input=str(number))
                dsdc.length = dsdc.length or data_type_object.default_length
                dsdc.data.extend(data_type_object.to_bytes(dsdc.length))
        else:
            dsdc.data = None
            dsdc.length = dsdc.length or DataType(dsdc.data_type).default_length
        # Start (after boundary alignment) and End (After duplication factor)
        dsdc.start = macro.location_counter + dsdc.align_to_boundary
        dsdc.end = dsdc.start + dsdc.duplication_factor * dsdc.length
        return dsdc, Error.NO_ERROR


class DirectiveImplementation:
    @staticmethod
    def ds(line, macro, name):
        data = macro.global_program.segments[macro.seg_name].data if macro.global_program else None
        operands = line.split_operands()
        dc, result = DsDc.from_operand(operands[0], macro)
        if result != Error.NO_ERROR:
            return result
        if line.label:
            dsp = data.next_constant if data and dc.duplication_factor == 0 and name == macro.seg_name else dc.start
            macro.data_map[line.label] = LabelReference(line.label, dsp, dc.length, name)
            if dc.duplication_factor == 0 and name == macro.seg_name:
                macro.data_map[line.label].set_branch()
        macro.location_counter = dc.end
        if len(operands) > 1:
            for operand in operands[1:]:
                dc, result = DsDc.from_operand(operand, macro)
                if result != Error.NO_ERROR:
                    return result
                macro.location_counter = dc.end
        macro.max_counter = macro.location_counter if macro.location_counter > macro.max_counter else macro.max_counter
        return Error.NO_ERROR

    @staticmethod
    def dc(line, macro, name):
        data = macro.global_program.segments[macro.seg_name].data if macro.global_program else None
        if data is None:
            raise TypeError
        operands = line.split_operands()
        dc, result = DsDc.from_operand(operands[0], macro)
        if result != Error.NO_ERROR:
            return result
        data.extend_constant([0x00] * dc.align_to_boundary)
        if line.label:
            macro.data_map[line.label] = LabelReference(line.label, data.next_constant, dc.length, name)
        macro.location_counter = dc.end
        data.extend_constant(dc.data * dc.duplication_factor)
        if len(operands) > 1:
            for operand in operands[1:]:
                dc, result = DsDc.from_operand(operand, macro)
                if result != Error.NO_ERROR:
                    return result
                macro.location_counter = dc.end
                data.extend_constant([0x00] * dc.align_to_boundary)
                data.extend_constant(dc.data * dc.duplication_factor)
        macro.max_counter = macro.location_counter if macro.location_counter > macro.max_counter else macro.max_counter
        return Error.NO_ERROR

    @staticmethod
    def equ(line, macro, name):
        if line.label is None:
            return Error.EQU_LABEL_REQUIRED
        operands = line.split_operands()
        dsp_operand = operands[0]
        length = 1
        if dsp_operand == '*':
            dsp = macro.location_counter
        elif not set("+-*").intersection(dsp_operand):
            if dsp_operand.isdigit():
                dsp = int(dsp_operand)
            elif re.match(r"^[CXHFDBZPAY]'[^']+'$", dsp_operand) is not None:
                if '&' in dsp_operand:
                    return Error.EQU_INVALID_VALUE
                dsp = DataType(dsp_operand[0], input=dsp_operand[2:-1]).value
            else:
                field, result = macro.lookup(dsp_operand)
                if result != Error.NO_ERROR:
                    return result
                dsp = field.dsp
                length = field.length
        else:
            dsp, result = macro.get_value(dsp_operand)
            if result != Error.NO_ERROR:
                return result
        if len(operands) > 1:
            length, result = macro.get_value(operands[1])
            if result != Error.NO_ERROR:
                return result
        macro.data_map[line.label] = LabelReference(line.label, dsp, length, name)
        if macro.location_counter == dsp and name == macro.seg_name:
            macro.data_map[line.label].set_branch()
        return Error.NO_ERROR

    @staticmethod
    def dsect(line, macro, **_):
        name = line.label
        seg_location_counter, _ = macro.dsect if macro.dsect is not None else (macro.location_counter, None)
        macro.dsect = seg_location_counter, name
        macro.location_counter = 0
        macro.max_counter = 0
        macro.data_map[name] = LabelReference(name, 0, 0, name)
        return Error.NO_ERROR

    @staticmethod
    def csect(line, macro, **_):
        dsect_location_counter, name = macro.dsect
        macro.dsect = None
        macro.location_counter = dsect_location_counter
        macro.max_counter = dsect_location_counter
        macro.data_map[line.label] = LabelReference(line.label, macro.location_counter, 0, name)
        return Error.NO_ERROR

    @staticmethod
    def org(line, macro, **_):
        if line.operand is None:
            macro.location_counter = macro.max_counter
            return Error.NO_ERROR
        else:
            macro.location_counter, result = macro.get_value(line.operand)
            if result != Error.NO_ERROR:
                raise TypeError
            return result

    @staticmethod
    def pgmid(macro, **_):
        macro.location_counter = 8
        return Error.NO_ERROR

    @staticmethod
    def push(macro, **_):
        macro.using_stack.append(macro.using.copy())
        return Error.NO_ERROR

    @staticmethod
    def pop(macro, **_):
        macro.using = macro.using_stack.pop()
        return Error.NO_ERROR

    @staticmethod
    def using(line, macro, name):
        operands = line.split_operands()
        if len(operands) == 2 and Register(operands[1]).is_valid():
            dsect = name if operands[0] == '*' else operands[0]
            macro.set_using(dsect, operands[1])
            return Error.NO_ERROR
        else:
            raise TypeError

    @staticmethod
    def no_operation(**_):
        return Error.NO_ERROR


class Literal:
    @staticmethod
    def update(literal, macro):
        if not literal.startswith('='):
            return literal
        literal, result = DsDc.from_operand(literal[1:], macro)
        if result != Error.NO_ERROR:
            raise AttributeError
        data = macro.global_program.segments[macro.seg_name].data
        dsp = data.next_literal + config.F4K
        data.extend_literal(literal.data * literal.duplication_factor)
        label = f"L{Label.SEPARATOR * 2}{dsp:05X}"
        macro.data_map[label] = LabelReference(label, dsp, literal.length, macro.seg_name)
        return label


class Directive:
    AD: Dict[str, callable] = {
        'DS': DirectiveImplementation.ds,
        'DC': DirectiveImplementation.dc,
        'EQU': DirectiveImplementation.equ,
        'DSECT': DirectiveImplementation.dsect,
        'CSECT': DirectiveImplementation.csect,
        'ORG': DirectiveImplementation.org,
        'PGMID': DirectiveImplementation.pgmid,
        'PUSH': DirectiveImplementation.push,
        'POP': DirectiveImplementation.pop,
        'USING': DirectiveImplementation.using,
        'LTORG': DirectiveImplementation.no_operation,
        'FINIS': DirectiveImplementation.no_operation,
        'END': DirectiveImplementation.no_operation,
    }

    @classmethod
    def second_pass(cls, directive_type: str, ad_list: List[Tuple[Line, int]], macro, name: str, errors: list):
        for line, location_counter in ad_list:
            if line.command != directive_type:
                continue
            macro.location_counter = location_counter
            result = cls.AD[line.command](line=line, macro=macro, name=name)
            if result != Error.NO_ERROR:
                errors.append(f'{result} {line} {name}')

    @classmethod
    def update(cls, line, macro, name):
        return cls.AD[line.command](line=line, macro=macro, name=name)
