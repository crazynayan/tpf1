import v2.instruction_type as ins


class L(ins.RegisterFieldIndex):
    def execute(self, state):
        address = state.regs.get_address(self.field.base, self.field.dsp, self.field.index)
        value = state.vm.get_value(address, 4)
        value = state.validate(value)
        state.regs.set_value(value, self.reg)


class LH(ins.RegisterFieldIndex):
    def execute(self, state):
        address = state.regs.get_address(self.field.base, self.field.dsp, self.field.index)
        value = state.vm.get_value(address, 2)
        state.regs.set_value(value, self.reg)


class N(ins.RegisterFieldIndex):
    def execute(self, state):
        address = state.regs.get_address(self.field.base, self.field.dsp, self.field.index)
        value = state.vm.get_value(address, 4)
        value &= state.regs.get_value(self.reg)
        state.regs.set_value(value, self.reg)


class STH(ins.RegisterFieldIndex):
    def execute(self, state):
        address = state.regs.get_address(self.field.base, self.field.dsp, self.field.index)
        value = state.regs.get_value(self.reg)
        state.vm.set_value(value, address, 2)


class LHI(ins.RegisterData):
    def execute(self, state):
        state.regs.set_value(self.data, self.reg)


class STC(ins.RegisterFieldIndex):
    def execute(self, state):
        address = state.regs.get_address(self.field.base, self.field.dsp, self.field.index)
        byte = state.regs.get_bytes_from_mask(self.reg, 0b0001)
        state.vm.set_bytes(byte, address)


class BACKC(ins.Exit):
    def execute(self, state):
        pass


class EQU(ins.InstructionGeneric):
    def execute(self, state):
        pass


class DS(ins.InstructionGeneric):
    def execute(self, state):
        pass


class Instruction:
    INS = {
        'EQU': EQU,
        'DS': DS,
        'NI': ins.FieldBits,
        'TM': ins.FieldBits,
        'OI': ins.FieldBits,
        'XI': ins.FieldBits,
        'MVC': ins.FieldLenField,
        'OC': ins.FieldLenField,
        'CLC': ins.FieldLenField,
        'XC': ins.FieldLenField,
        'MVZ': ins.FieldLenField,
        'MVN': ins.FieldLenField,
        'TR': ins.FieldLenField,
        'TRT': ins.FieldLenField,
        'ED': ins.FieldLenField,
        'EDMK': ins.FieldLenField,
        'NC': ins.FieldLenField,
        'UNPK': ins.FieldLenFieldLen,
        'PACK': ins.FieldLenFieldLen,
        'ZAP': ins.FieldLenFieldLen,
        'AP': ins.FieldLenFieldLen,
        'SP': ins.FieldLenFieldLen,
        'MP': ins.FieldLenFieldLen,
        'DP': ins.FieldLenFieldLen,
        'CP': ins.FieldLenFieldLen,
        'MVO': ins.FieldLenFieldLen,
        'SRP': ins.FieldLenFieldData,
        'CLI': ins.FieldData,
        'MVI': ins.FieldData,
        'TP': ins.FieldSingle,
        'BCTR': ins.RegisterRegister,
        'LR': ins.RegisterRegister,
        'LTR': ins.RegisterRegister,
        'AR': ins.RegisterRegister,
        'SR': ins.RegisterRegister,
        'LPR': ins.RegisterRegister,
        'LNR': ins.RegisterRegister,
        'LCR': ins.RegisterRegister,
        'MR': ins.RegisterRegister,
        'DR': ins.RegisterRegister,
        'MVCL': ins.RegisterRegister,
        'BASR': ins.RegisterRegister,
        'CR': ins.RegisterRegister,
        'CLR': ins.RegisterRegister,
        'NR': ins.RegisterRegister,
        'OR': ins.RegisterRegister,
        'XR': ins.RegisterRegister,
        'CLCL': ins.RegisterRegister,
        'ALR': ins.RegisterRegister,
        'SLR': ins.RegisterRegister,
        'CVB': ins.RegisterFieldIndex,
        'STH': STH,
        'LH': LH,
        'A': ins.RegisterFieldIndex,
        'AH': ins.RegisterFieldIndex,
        'S': ins.RegisterFieldIndex,
        'SH': ins.RegisterFieldIndex,
        'MH': ins.RegisterFieldIndex,
        'M': ins.RegisterFieldIndex,
        'D': ins.RegisterFieldIndex,
        'SLA': ins.RegisterFieldIndex,
        'SRA': ins.RegisterFieldIndex,
        'SLDA': ins.RegisterFieldIndex,
        'SRDA': ins.RegisterFieldIndex,
        'SLL': ins.RegisterFieldIndex,
        'SRL': ins.RegisterFieldIndex,
        'SLDL': ins.RegisterFieldIndex,
        'SRDL': ins.RegisterFieldIndex,
        'C': ins.RegisterFieldIndex,
        'CL': ins.RegisterFieldIndex,
        'AL': ins.RegisterFieldIndex,
        'SL': ins.RegisterFieldIndex,
        'O': ins.RegisterFieldIndex,
        'X': ins.RegisterFieldIndex,
        'L': L,
        'IC': ins.RegisterFieldIndex,
        'STC': STC,
        'N': N,
        'LA': ins.RegisterFieldIndex,
        'CH': ins.RegisterFieldIndex,
        'ST': ins.RegisterFieldIndex,
        'CVD': ins.RegisterFieldIndex,
        'LHI': LHI,
        'AHI': ins.RegisterData,
        'MHI': ins.RegisterData,
        'CHI': ins.RegisterData,
        'LM': ins.RegisterRegisterField,
        'STM': ins.RegisterRegisterField,
        'CLM': ins.RegisterDataField,
        'ICM': ins.RegisterDataField,
        'STCM': ins.RegisterDataField,
        'BAS': ins.RegisterBranch,
        'JAS': ins.RegisterBranch,
        'BCT': ins.RegisterBranch,
        'EX': ins.RegisterLabel,
        'BXH': ins.RegisterRegisterBranch,
        'BXLE': ins.RegisterRegisterBranch,
        'EXITC': ins.Exit,
        'BACKC': BACKC,
        'B': ins.BranchCondition,
        'J': ins.BranchCondition,
        'BE': ins.BranchCondition,
        'BNE': ins.BranchCondition,
        'BH': ins.BranchCondition,
        'BNH': ins.BranchCondition,
        'BL': ins.BranchCondition,
        'BNL': ins.BranchCondition,
        'BM': ins.BranchCondition,
        'BNM': ins.BranchCondition,
        'BP': ins.BranchCondition,
        'BNP': ins.BranchCondition,
        'BC': ins.BranchCondition,
        'BCRY': ins.BranchCondition,
        'BO': ins.BranchCondition,
        'BNO': ins.BranchCondition,
        'BZ': ins.BranchCondition,
        'BNZ': ins.BranchCondition,
        'JE': ins.BranchCondition,
        'JNE': ins.BranchCondition,
        'JH': ins.BranchCondition,
        'JNH': ins.BranchCondition,
        'JL': ins.BranchCondition,
        'JNL': ins.BranchCondition,
        'JM': ins.BranchCondition,
        'JNM': ins.BranchCondition,
        'JP': ins.BranchCondition,
        'JNP': ins.BranchCondition,
        'JC': ins.BranchCondition,
        'JO': ins.BranchCondition,
        'JNO': ins.BranchCondition,
        'JZ': ins.BranchCondition,
        'JNZ': ins.BranchCondition,
        'NOP': ins.BranchCondition,
        'JNOP': ins.BranchCondition,
        'BR': ins.BranchConditionRegister,
        'BER': ins.BranchConditionRegister,
        'BNER': ins.BranchConditionRegister,
        'BHR': ins.BranchConditionRegister,
        'BNHR': ins.BranchConditionRegister,
        'BLR': ins.BranchConditionRegister,
        'BNLR': ins.BranchConditionRegister,
        'BMR': ins.BranchConditionRegister,
        'BNMR': ins.BranchConditionRegister,
        'BPR': ins.BranchConditionRegister,
        'BNPR': ins.BranchConditionRegister,
        'BCR': ins.BranchConditionRegister,
        'BOR': ins.BranchConditionRegister,
        'BNOR': ins.BranchConditionRegister,
        'BZR': ins.BranchConditionRegister,
        'BNZR': ins.BranchConditionRegister,
        'NOPR': ins.BranchConditionRegister,
        'ENTRC': ins.SegmentCall,
        'ENTNC': ins.SegmentCall,
        'ENTDC': ins.SegmentCall,
        'AAGET': ins.KeyValue,
        'GETCC': ins.KeyValue,
        'PNRCC': ins.KeyValue,
        'MODEC': ins.KeyValue,
        'DETAC': ins.KeyValue,
        'DBOPN': ins.KeyValue,
        'PDCLS': ins.KeyValue,
        'ATTAC': ins.KeyValue,
        'RELCC': ins.KeyValue,
        'CRUSA': ins.KeyValue,
        'PNRCM': ins.KeyValue,
        'GLOBZ': ins.Globz,
        'SYSRA': ins.KeyValue,
        'DBRED': ins.KeyValue,
        'SENDA': ins.KeyValue,
        'CFCMA': ins.KeyValue,
        'SERRC': ins.KeyValue,
        'DBCLS': ins.KeyValue,
        'DBIFB': ins.KeyValue,
        'PDRED': ins.KeyValue,
        'LTORG': ins.KeyValue,
        'FINIS': ins.KeyValue,
        'END': ins.KeyValue,
    }

    def __init__(self, ins_type):
        if ins_type not in self.INS:
            raise KeyError
        self.instruction_object = self.INS[ins_type]()

    def create(self, line, macro):
        self.instruction_object.label = line.label
        self.instruction_object.command = line.command
        return self.instruction_object.set_operand(line, macro)

    @classmethod
    def from_line(cls, line, macro):
        instruction_object = cls(line.command)
        return instruction_object.create(line, macro)
