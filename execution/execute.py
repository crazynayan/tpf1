from typing import Dict, Callable

from assembly.seg3_ins_type import InstructionType
from execution.db_macro import DbMacro
from execution.executable_macro import ExecutableMacro
from execution.instruction import Instruction


class Execute(Instruction, ExecutableMacro, DbMacro):
    def __init__(self):
        super().__init__()
        self.ex: Dict[str, Callable] = {

            # S03 - Load & Store
            'LR': self.load_register,
            'LTR': self.load_test_register,
            # LPR - Not in ETA5
            # LNR - Not in ETA5
            # LCR - Not in ETA5
            'L': self.load_fullword,
            'ST': self.store_fullword,
            'LA': self.load_address,
            'LH': self.load_halfword,
            'LHI': self.load_halfword_immediate,
            'STH': self.store_halfword,
            'IC': self.insert_character,
            'ICM': self.insert_character_mask,
            'STC': self.store_character,
            'STCM': self.store_character_mask,
            'LM': self.load_multiple,
            'STM': self.store_multiple,

            # S04 - Arithmetic & Shift Algebraic
            'AR': self.add_register,
            # A - Not in ETA5
            'AH': self.add_halfword,
            'AHI': self.add_halfword_immediate,
            'SR': self.subtract_register,
            # S - Not in ETA5
            # SH - Not in ETA5
            # MH, MHI, M, MR, DR, D - Not in ETA5
            # SLA, SRA, SLDA, SRDA - Not in ETA5

            # S05 - Move Store & Logic Control
            'MVC': self.move_character,
            'MVI': self.move_immediate,
            # MVCL - Not in ETA5
            # MVZ, MVO, MVN - Not in ETA5
            'B': self.branch,
            'J': self.branch,
            'BCT': self.branch_on_count,
            'BCTR': self.branch_on_count_register,
            # BXH, BXLE - Not in ETA5
            'BAS': self.branch_and_save,
            'BR': self.branch_return,
            # BASR - Not in ETA5

            # S06 -  Compare & Logical
            'CR': self.compare_register,
            'C': self.compare_fullword,
            'CH': self.compare_halfword,
            # CHI - Not in ETA5
            # CL, CLR - Not in ETA5
            'CLI': self.compare_logical_immediate,
            'CLC': self.compare_logical_character,
            # CLM, CLCL - Not in ETA5
            # SLL, SRL, SLDL, SRDL - Not in ETA5
            # ALR, AL, SLR, SL - Not in ETA5


            # S07 - And/Or/Xor, TM, EX, Data Conversion
            # NR - Not in ETA5
            # XR - Not in ETA5
            'OR': self.or_register,
            'N': self.and_fullword,
            # O - Not in ETA5
            # X - Not in ETA5
            'NC': self.and_character,
            'OC': self.or_character,
            'XC': self.xor_character,
            'NI': self.and_immediate,
            'OI': self.or_immediate,
            # XI - Not in ETA5 (Need to check the status of flipped bits via is_updated_bit)
            'TM': self.test_mask,
            'EX': self.execute,
            'PACK': self.pack,
            'CVB': self.convert_binary,
            'CVD': self.convert_decimal,
            'UNPK': self.unpack,

            # S08 - Decimal Arithmetic & Complex - Not in ETA5
            # ZAP
            # AP
            # SP
            # MP, DP, SRP
            # CP
            # TP
            # TR
            # TRT
            # ED, EDMK

            # Realtime Macros
            'GETCC': self.getcc,
            'MODEC': self.no_operation,
            'DETAC': self.detac,
            'ATTAC': self.attac,
            'RELCC': self.relcc,
            'CRUSA': self.crusa,
            'SENDA': self.senda,
            'SYSRA': self.sysra,
            'SERRC': self.serrc,
            'ENTRC': self.entrc,
            'ENTNC': self.entnc,
            'ENTDC': self.entdc,
            'BACKC': self.backc,

            # User Defined Executable Macros
            'AAGET': self.aaget,
            'CFCMA': self.heapa,
            'HEAPA': self.heapa,
            'PNRCC': self.pnrcc,

            # User Defined Executable Macros created for this tool
            'PARS_DATE': self.pars_date,
            'ERROR_CHECK': self.error_check,

            # Realtime Db Macros - Not in ETA5
            'FINWC': self.finwc,
            # FINWC, FIWHC, FINDC, FINHC
            # FILEC, FILNC

            # User defined Db Macros
            'PDRED': self.pdred,
            'PDCLS': self.pdcls,
            # PDADD, PDDEL - Not in ETA5

            # TPFDF Macros
            'DBOPN': self.dbopn,
            'DBRED': self.dbred,
            'DBCLS': self.dbcls,
            'DBIFB': self.dbifb,
            # DBADD, DBDEL - Not in ETA5

            # No operation
            'EQU': self.no_operation,
            'DS': self.no_operation,
            'EXITC': self.no_operation,
        }

    def no_operation(self, node: InstructionType) -> str:
        return self.next_label(node)
