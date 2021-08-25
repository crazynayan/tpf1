from typing import Dict

from config import config
from p1_utils.data_type import Register
from p1_utils.errors import DataInvalidError, RegisterInvalidError, ConditionMaskError, AssemblyError, \
    BranchInvalidError, NotFoundInSymbolTableError
from p1_utils.file_line import Line
from p2_assembly.seg2_ins_operand import InstructionOperand
from p2_assembly.seg3_ins_type import InstructionGeneric, FieldBits, FieldLenField, FieldLenFieldLen, FieldData, \
    RegisterRegister, RegisterFieldIndex, RegisterData, RegisterRegisterField, RegisterDataField, BranchCondition, \
    RegisterBranch, BranchConditionRegister, FieldSingle, RegisterRegisterBranch, InstructionType, \
    FieldLenFieldData, BranchGeneric, FieldSingleBaseDsp


class InstructionImplementation(InstructionOperand):

    def __init__(self, name: str):
        super().__init__(name)
        self.nodes: Dict[str, InstructionType] = dict()
        self._command["OI"] = self.field_bits
        self._command["NI"] = self.field_bits
        self._command["XI"] = self.field_bits
        self._command["TM"] = self.field_bits
        self._command["CLC"] = self.field_len_field
        self._command["MVC"] = self.field_len_field
        self._command["XC"] = self.field_len_field
        self._command["OC"] = self.field_len_field
        self._command["NC"] = self.field_len_field
        self._command["MVZ"] = self.field_len_field
        self._command["MVN"] = self.field_len_field
        self._command["TRT"] = self.field_len_field
        self._command["TR"] = self.field_len_field
        self._command["ED"] = self.field_len_field
        self._command["EDMK"] = self.field_len_field
        self._command["PACK"] = self.field_len_field_len
        self._command["UNPK"] = self.field_len_field_len
        self._command["MVO"] = self.field_len_field_len
        self._command["ZAP"] = self.field_len_field_len
        self._command["AP"] = self.field_len_field_len
        self._command["SP"] = self.field_len_field_len
        self._command["DP"] = self.field_len_field_len
        self._command["MP"] = self.field_len_field_len
        self._command["CP"] = self.field_len_field_len
        self._command["SRP"] = self.field_len_field_data
        self._command["TP"] = self.field_single
        self._command["STCK"] = self.field_single_base_dsp
        self._command["CLI"] = self.field_data
        self._command["CLHHSI"] = self.field_data
        self._command["MVI"] = self.field_data
        self._command["MVHHI"] = self.field_data
        self._command["LTR"] = self.reg_reg
        self._command["LR"] = self.reg_reg
        self._command["AR"] = self.reg_reg
        self._command["SR"] = self.reg_reg
        self._command["MR"] = self.reg_reg
        self._command["DR"] = self.reg_reg
        self._command["ALR"] = self.reg_reg
        self._command["SLR"] = self.reg_reg
        self._command["BCTR"] = self.reg_reg
        self._command["LPR"] = self.reg_reg
        self._command["LNR"] = self.reg_reg
        self._command["LCR"] = self.reg_reg
        self._command["MVCL"] = self.reg_reg
        self._command["CLCL"] = self.reg_reg
        self._command["CLR"] = self.reg_reg
        self._command["CR"] = self.reg_reg
        self._command["NR"] = self.reg_reg
        self._command["OR"] = self.reg_reg
        self._command["XR"] = self.reg_reg
        self._command["XGR"] = self.reg_reg
        self._command["BASR"] = self.reg_reg
        self._command["LG"] = self.reg_field_index
        self._command["L"] = self.reg_field_index
        self._command["LH"] = self.reg_field_index
        self._command["LA"] = self.reg_field_index
        self._command["LARL"] = self.reg_field_index
        self._command["IC"] = self.reg_field_index
        self._command["LLC"] = self.reg_field_index
        self._command["STH"] = self.reg_field_index
        self._command["N"] = self.reg_field_index
        self._command["O"] = self.reg_field_index
        self._command["X"] = self.reg_field_index
        self._command["ST"] = self.reg_field_index
        self._command["STG"] = self.reg_field_index
        self._command["STC"] = self.reg_field_index
        self._command["CVB"] = self.reg_field_index
        self._command["CVD"] = self.reg_field_index
        self._command["CH"] = self.reg_field_index
        self._command["C"] = self.reg_field_index
        self._command["CL"] = self.reg_field_index
        self._command["A"] = self.reg_field_index
        self._command["AH"] = self.reg_field_index
        self._command["AL"] = self.reg_field_index
        self._command["S"] = self.reg_field_index
        self._command["SH"] = self.reg_field_index
        self._command["SL"] = self.reg_field_index
        self._command["MH"] = self.reg_field_index
        self._command["M"] = self.reg_field_index
        self._command["D"] = self.reg_field_index
        self._command["SLA"] = self.reg_field_index
        self._command["SRDA"] = self.reg_field_index
        self._command["SRA"] = self.reg_field_index
        self._command["SLDA"] = self.reg_field_index
        self._command["SLL"] = self.reg_field_index
        self._command["SRL"] = self.reg_field_index
        self._command["SLDL"] = self.reg_field_index
        self._command["SRDL"] = self.reg_field_index
        self._command["AFI"] = self.reg_data
        self._command["AHI"] = self.reg_data
        self._command["LHI"] = self.reg_data
        self._command["CHI"] = self.reg_data
        self._command["MHI"] = self.reg_data
        self._command["LM"] = self.reg_reg_field
        self._command["STM"] = self.reg_reg_field
        self._command["ICM"] = self.reg_data_field
        self._command["STCM"] = self.reg_data_field
        self._command["CLM"] = self.reg_data_field
        self._command["BAS"] = self.reg_branch
        self._command["BAL"] = self.reg_branch
        self._command["JAS"] = self.reg_branch
        self._command["BCT"] = self.reg_branch
        self._command["JCT"] = self.reg_branch
        self._command["BXH"] = self.reg_reg_branch
        self._command["BXLE"] = self.reg_reg_branch
        self._command["EX"] = self.reg_label
        self._command["BC"] = self.branch_condition
        self._command["B"] = self.branch_mnemonic
        self._command["NOP"] = self.branch_mnemonic
        self._command["BZ"] = self.branch_mnemonic
        self._command["BNZ"] = self.branch_mnemonic
        self._command["BO"] = self.branch_mnemonic
        self._command["BNO"] = self.branch_mnemonic
        self._command["BE"] = self.branch_mnemonic
        self._command["BNE"] = self.branch_mnemonic
        self._command["BM"] = self.branch_mnemonic
        self._command["BNM"] = self.branch_mnemonic
        self._command["BP"] = self.branch_mnemonic
        self._command["BNP"] = self.branch_mnemonic
        self._command["BH"] = self.branch_mnemonic
        self._command["BNH"] = self.branch_mnemonic
        self._command["BL"] = self.branch_mnemonic
        self._command["BNL"] = self.branch_mnemonic
        self._command["JC"] = self.branch_condition
        self._command["J"] = self.branch_mnemonic
        self._command["JNOP"] = self.branch_mnemonic
        self._command["JZ"] = self.branch_mnemonic
        self._command["JNZ"] = self.branch_mnemonic
        self._command["JO"] = self.branch_mnemonic
        self._command["JNO"] = self.branch_mnemonic
        self._command["JE"] = self.branch_mnemonic
        self._command["JNE"] = self.branch_mnemonic
        self._command["JM"] = self.branch_mnemonic
        self._command["JNM"] = self.branch_mnemonic
        self._command["JP"] = self.branch_mnemonic
        self._command["JNP"] = self.branch_mnemonic
        self._command["JH"] = self.branch_mnemonic
        self._command["JNH"] = self.branch_mnemonic
        self._command["JL"] = self.branch_mnemonic
        self._command["JNL"] = self.branch_mnemonic
        self._command["BCR"] = self.branch_condition_reg
        self._command["BR"] = self.branch_mnemonic_reg
        self._command["NOPR"] = self.branch_mnemonic_reg
        self._command["BER"] = self.branch_mnemonic_reg
        self._command["BNER"] = self.branch_mnemonic_reg
        self._command["BHR"] = self.branch_mnemonic_reg
        self._command["BNHR"] = self.branch_mnemonic_reg
        self._command["BLR"] = self.branch_mnemonic_reg
        self._command["BNLR"] = self.branch_mnemonic_reg
        self._command["BZR"] = self.branch_mnemonic_reg
        self._command["BNZR"] = self.branch_mnemonic_reg
        self._command["BOR"] = self.branch_mnemonic_reg
        self._command["BNOR"] = self.branch_mnemonic_reg
        self._command["BPR"] = self.branch_mnemonic_reg
        self._command["BNPR"] = self.branch_mnemonic_reg
        self._command["BMR"] = self.branch_mnemonic_reg
        self._command["BNMR"] = self.branch_mnemonic_reg

    @staticmethod
    def instruction_generic(line: Line) -> InstructionGeneric:
        return InstructionGeneric(line)

    def equ(self, line: Line) -> InstructionGeneric:
        if not self.check(line.label):
            super().equ(line)
        return InstructionGeneric(line)

    def ds(self, line: Line) -> InstructionGeneric:
        if not self.check(line.label):
            super().ds(line)
        return InstructionGeneric(line)

    def field_bits(self, line: Line) -> FieldBits:
        try:
            operand1, operand2 = line.split_operands()
        except ValueError:
            raise AssemblyError(line)
        try:
            field = self.field_base_dsp(operand1)
        except NotFoundInSymbolTableError:
            raise NotFoundInSymbolTableError(line)
        bits = self.get_bits(operand2)
        return FieldBits(line, field, bits)

    def field_len_field(self, line: Line) -> FieldLenField:
        try:
            operand1, operand2 = line.split_operands()
        except ValueError:
            raise AssemblyError(line)
        field_len = self.field_len(operand1, FieldLenField.MAX_LEN)
        try:
            field = self.field_base_dsp(operand2)
        except NotFoundInSymbolTableError:
            raise NotFoundInSymbolTableError(line)
        return FieldLenField(line, field_len, field)

    def field_len_field_len(self, line: Line) -> FieldLenFieldLen:
        operand1, operand2 = line.split_operands()
        field_len1 = self.field_len(operand1, FieldLenFieldLen.MAX_LEN)
        field_len2 = self.field_len(operand2, FieldLenFieldLen.MAX_LEN)
        return FieldLenFieldLen(line, field_len1, field_len2)

    def field_data(self, line: Line) -> FieldData:
        operand1, operand2 = line.split_operands()
        try:
            field = self.field_base_dsp(operand1)
        except NotFoundInSymbolTableError:
            raise NotFoundInSymbolTableError(line)
        data = self.get_value(operand2)
        if not 0 <= data <= FieldData.MAX_VALUE:
            raise DataInvalidError
        return FieldData(line, field, data)

    def field_single(self, line: Line) -> FieldSingle:
        field = self.field_len(line.operand, FieldSingle.MAX_LEN)
        return FieldSingle(line, field)

    def field_single_base_dsp(self, line: Line) -> FieldSingleBaseDsp:
        field = self.field_base_dsp(line.operand)
        return FieldSingleBaseDsp(line, field)

    def field_len_field_data(self, line: Line) -> FieldLenFieldData:
        operand1, operand2, operand3 = line.split_operands()
        field_len = self.field_len(operand1, FieldLenFieldData.MAX_LEN)
        field = self.field_base_dsp(operand2)
        data = self.get_value(operand3)
        if not 0 <= data <= FieldLenFieldData.MAX_VALUE:
            raise DataInvalidError
        return FieldLenFieldData(line, field_len, field, data)

    @staticmethod
    def reg_reg(line: Line) -> RegisterRegister:
        operand1, operand2 = line.split_operands()
        reg1 = Register(operand1)
        reg2 = Register(operand2)
        if not reg1.is_valid() or not reg2.is_valid():
            raise RegisterInvalidError
        return RegisterRegister(line, reg1, reg2)

    def reg_field_index(self, line: Line) -> RegisterFieldIndex:
        operand1, operand2 = line.split_operands()
        reg = Register(operand1)
        if not reg.is_valid():
            raise RegisterInvalidError(line)
        try:
            field = self.field_index(operand2)
        except RegisterInvalidError:
            raise RegisterInvalidError(line)
        except NotFoundInSymbolTableError:
            raise NotFoundInSymbolTableError(line)
        return RegisterFieldIndex(line, reg, field)

    def reg_data(self, line: Line) -> RegisterData:
        operand1, operand2 = line.split_operands()
        reg = Register(operand1)
        if not reg.is_valid():
            raise RegisterInvalidError
        data = self.get_value(operand2)
        max_unsigned_value = (1 << RegisterData.DATA_LENGTH) - 1
        min_signed_value = -1 << RegisterData.DATA_LENGTH - 1
        max_signed_value = (1 << RegisterData.DATA_LENGTH - 1) - 1
        if not min_signed_value <= data <= max_unsigned_value:
            raise DataInvalidError((line, data))
        if data > max_signed_value:
            data -= max_unsigned_value + 1  # Two"s complement negative number
        return RegisterData(line, reg, data)

    def reg_reg_field(self, line: Line) -> RegisterRegisterField:
        operand1, operand2, operand3 = line.split_operands()
        reg1 = Register(operand1)
        reg2 = Register(operand2)
        if not reg1.is_valid() or not reg2.is_valid():
            raise RegisterInvalidError
        field = self.field_base_dsp(operand3)
        return RegisterRegisterField(line, reg1, reg2, field)

    def reg_data_field(self, line: Line) -> RegisterDataField:
        operand1, operand2, operand3 = line.split_operands()
        reg = Register(operand1)
        if not reg.is_valid():
            raise RegisterInvalidError
        data = self.get_value(operand2)
        if not 0 <= data <= RegisterDataField.MAX_VALUE:
            raise DataInvalidError
        field = self.field_base_dsp(operand3)
        return RegisterDataField(line, reg, data, field)

    def branch_condition(self, line: Line) -> BranchCondition:
        operand1, operand2 = line.split_operands()
        mask = self.get_value(operand1)
        if not 0 <= mask <= BranchGeneric.MAX_VALUE:
            raise ConditionMaskError
        branch = self.get_branch(operand2)
        return BranchCondition(line, branch, mask)

    def branch_mnemonic(self, line: Line) -> BranchCondition:
        mask = config.MASK[line.command]
        try:
            branch = self.get_branch(line.operand)
        except BranchInvalidError:
            raise BranchInvalidError(line)
        return BranchCondition(line, branch, mask)

    @staticmethod
    def branch_mnemonic_reg(line: Line) -> BranchConditionRegister:
        mask = config.MASK[line.command]
        reg = Register(line.operand)
        if not reg.is_valid():
            raise RegisterInvalidError
        return BranchConditionRegister(line, mask, reg)

    def branch_condition_reg(self, line: Line) -> BranchConditionRegister:
        operand1, operand2 = line.split_operands()
        mask = self.get_value(operand1)
        if not 0 <= mask <= BranchGeneric.MAX_VALUE:
            raise ConditionMaskError
        reg = Register(operand2)
        if not reg.is_valid():
            raise RegisterInvalidError
        return BranchConditionRegister(line, mask, reg)

    def reg_branch(self, line: Line) -> RegisterBranch:
        operand1, operand2 = line.split_operands()
        reg = Register(operand1)
        if not reg.is_valid():
            raise RegisterInvalidError
        branch = self.get_branch(operand2)
        return RegisterBranch(line, reg, branch)

    def reg_reg_branch(self, line: Line) -> RegisterRegisterBranch:
        operand1, operand2, operand3 = line.split_operands()
        reg1 = Register(operand1)
        reg2 = Register(operand2)
        if not reg1.is_valid() or not reg2.is_valid():
            raise RegisterInvalidError
        branch = self.get_branch(operand3)
        return RegisterRegisterBranch(line, reg1, reg2, branch)

    def reg_label(self, line: Line) -> RegisterFieldIndex:
        reg_index: RegisterFieldIndex = self.reg_field_index(line)
        _, operand2 = line.split_operands()
        if operand2.startswith("*"):
            expression = line.label + operand2[1:]
            reg_index.field.dsp = self.get_value(expression)
            reg_index.field.base = Register("R8")
            reg_index.field.name = self.get_field_name(reg_index.field.base, reg_index.field.dsp, 4)
        return reg_index
