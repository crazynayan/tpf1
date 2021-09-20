from typing import Dict

from p2_assembly.seg3_ins_type import InstructionType
from p4_execution.ex2_instruction import Instruction
from p4_execution.ex3_executable_macro import ExecutableMacro
from p4_execution.ex4_db_macro import DbMacro


class TpfServer(Instruction, ExecutableMacro, DbMacro):
    def __init__(self):
        super().__init__()
        self._ex: Dict[str, callable] = dict()

        # S03 - Load & Store
        self._ex["LR"] = self.load_register
        self._ex["LTR"] = self.load_test_register
        # LPR, LNR - Not in ETA5
        # LCR - Not in ETA5
        self._ex["L"] = self.load_fullword
        self._ex["ST"] = self.store_fullword
        self._ex["LA"] = self.load_address
        self._ex["LARL"] = self.load_address
        self._ex["LH"] = self.load_halfword
        self._ex["LHI"] = self.load_halfword_immediate
        self._ex["STH"] = self.store_halfword
        self._ex["IC"] = self.insert_character
        self._ex["ICM"] = self.insert_character_mask
        self._ex["STC"] = self.store_character
        self._ex["STCM"] = self.store_character_mask
        self._ex["LM"] = self.load_multiple
        self._ex["STM"] = self.store_multiple

        # S04 - Arithmetic & Shift Algebraic
        self._ex["AR"] = self.add_register
        self._ex["A"] = self.add_fullword
        self._ex["AH"] = self.add_halfword
        self._ex["AHI"] = self.add_halfword_immediate
        self._ex["SR"] = self.subtract_register
        self._ex["S"] = self.subtract_fullword
        self._ex["SH"] = self.subtract_halfword
        self._ex["M"] = self.multiply_fullword
        self._ex["MH"] = self.multiply_halfword
        self._ex["MHI"] = self.multiply_halfword_immediate
        self._ex["D"] = self.divide_fullword
        self._ex["DR"] = self.divide_register
        self._ex["SRDA"] = self.shift_right_double_algebraic
        # MH, M, MR - Not in ETA5
        # SLA, SRA, SLDA - Not in ETA5

        # S05 - Move Store & Logic Control
        self._ex["MVC"] = self.move_character
        self._ex["MVI"] = self.move_immediate
        self._ex["MVCL"] = self.move_character_long
        self._ex["MVN"] = self.move_numeric
        self._ex["MVZ"] = self.move_zone
        # MVO
        self._ex["BCT"] = self.branch_on_count
        self._ex["JCT"] = self.branch_on_count
        self._ex["BCTR"] = self.branch_on_count_register
        self._ex["BXLE"] = self.branch_on_index_low_or_equal
        # BXH
        self._ex["BAS"] = self.branch_and_save
        self._ex["BAL"] = self.branch_and_save
        self._ex["JAS"] = self.branch_and_save
        # BASR
        self._ex["B"] = self.branch
        self._ex["NOP"] = self.branch
        self._ex["BZ"] = self.branch
        self._ex["BNZ"] = self.branch
        self._ex["BO"] = self.branch
        self._ex["BNO"] = self.branch
        self._ex["BE"] = self.branch
        self._ex["BNE"] = self.branch
        self._ex["BM"] = self.branch
        self._ex["BNM"] = self.branch
        self._ex["BP"] = self.branch
        self._ex["BNP"] = self.branch
        self._ex["BH"] = self.branch
        self._ex["BNH"] = self.branch
        self._ex["BL"] = self.branch
        self._ex["BNL"] = self.branch
        self._ex["JC"] = self.branch
        self._ex["J"] = self.branch
        self._ex["JNOP"] = self.branch
        self._ex["JZ"] = self.branch
        self._ex["JNZ"] = self.branch
        self._ex["JO"] = self.branch
        self._ex["JNO"] = self.branch
        self._ex["JE"] = self.branch
        self._ex["JNE"] = self.branch
        self._ex["JM"] = self.branch
        self._ex["JNM"] = self.branch
        self._ex["JP"] = self.branch
        self._ex["JNP"] = self.branch
        self._ex["JH"] = self.branch
        self._ex["JNH"] = self.branch
        self._ex["JL"] = self.branch
        self._ex["JNL"] = self.branch
        self._ex["BCR"] = self.branch_return
        self._ex["BR"] = self.branch_return
        self._ex["NOPR"] = self.branch_return
        self._ex["BER"] = self.branch_return
        self._ex["BNER"] = self.branch_return
        self._ex["BHR"] = self.branch_return
        self._ex["BNHR"] = self.branch_return
        self._ex["BLR"] = self.branch_return
        self._ex["BNLR"] = self.branch_return
        self._ex["BZR"] = self.branch_return
        self._ex["BNZR"] = self.branch_return
        self._ex["BOR"] = self.branch_return
        self._ex["BNOR"] = self.branch_return
        self._ex["BPR"] = self.branch_return
        self._ex["BNPR"] = self.branch_return
        self._ex["BMR"] = self.branch_return
        self._ex["BNMR"] = self.branch_return

        # S06 -  Compare & Logical
        self._ex["CR"] = self.compare_register
        self._ex["C"] = self.compare_fullword
        self._ex["CH"] = self.compare_halfword
        self._ex["CHI"] = self.compare_halfword_immediate
        # CL, CLR - Not in ETA5
        self._ex["CLI"] = self.compare_logical_immediate
        self._ex["CLC"] = self.compare_logical_character
        self._ex["CLM"] = self.compare_logical_character_mask
        # CLM, CLCL - Not in ETA5
        self._ex["SLL"] = self.shift_left_logical
        self._ex["SRL"] = self.shift_right_logical
        self._ex["SLDL"] = self.shift_left_double_logical
        self._ex["SRDL"] = self.shift_right_double_logical
        # ALR, AL, SLR, SL - Not in ETA5

        # S07 - And/Or/Xor, TM, EX, Data Conversion
        self._ex["OR"] = self.or_register
        self._ex["NR"] = self.and_register
        self._ex["XR"] = self.xor_register
        self._ex["N"] = self.and_fullword
        # O - Not in ETA5
        # X - Not in ETA5
        self._ex["NC"] = self.and_character
        self._ex["OC"] = self.or_character
        self._ex["XC"] = self.xor_character
        self._ex["NI"] = self.and_immediate
        self._ex["OI"] = self.or_immediate
        # XI - Not in ETA5 (Need to check the status of flipped bits via is_updated_bit)
        self._ex["TM"] = self.test_mask
        self._ex["EX"] = self.execute
        self._ex["PACK"] = self.pack
        self._ex["CVB"] = self.convert_binary
        self._ex["CVD"] = self.convert_decimal
        self._ex["UNPK"] = self.unpack

        # S08 - Decimal Arithmetic & Complex
        self._ex["ZAP"] = self.zap
        self._ex["AP"] = self.ap
        self._ex["SP"] = self.sp
        self._ex["MP"] = self.mp
        self._ex["DP"] = self.dp
        # SRP
        # CP
        self._ex["TP"] = self.tp
        self._ex["TR"] = self.tr
        # ED, EDMK, TRT, STCK

        # S09 - All new z/TPF instruction
        self._ex["LG"] = self.load_grande
        self._ex["STG"] = self.store_grande
        self._ex["XGR"] = self.xor_grande_register

        # Realtime Macros
        self._ex["GETCC"] = self.getcc
        self._ex["LEVTA"] = self.levta
        self._ex["MODEC"] = self.no_operation
        self._ex["DETAC"] = self.detac
        self._ex["ATTAC"] = self.attac
        self._ex["RELCC"] = self.relcc
        self._ex["RCUNC"] = self.relcc
        self._ex["RELFC"] = self.no_operation
        self._ex["RLCHA"] = self.no_operation
        self._ex["CRUSA"] = self.crusa
        self._ex["SENDA"] = self.senda
        self._ex["SYSRA"] = self.sysra
        self._ex["SERRC"] = self.serrc
        self._ex["SNAPC"] = self.snapc
        self._ex["ENTRC"] = self.entrc
        self._ex["ENTNC"] = self.entnc
        self._ex["ENTDC"] = self.entdc
        self._ex["BACKC"] = self.backc
        self._ex["ALASC"] = self.alasc
        self._ex["PNAMC"] = self.pnamc
        self._ex["FLIPC"] = self.flipc
        self._ex["EOWNRC"] = self.no_operation
        self._ex["CREMC"] = self.no_operation
        self._ex["GLBLC"] = self.no_operation
        self._ex["DLAYC"] = self.no_operation
        self._ex["DEFRC"] = self.no_operation
        self._ex["REALTIMA"] = self.realtima
        self._ex["MALOC"] = self.maloc

        # SPM Macros
        self._ex["#PERF"] = self.no_operation
        self._ex["#SPM"] = self.no_operation

        # User Defined Executable Macros
        self._ex["AAGET"] = self.aaget
        self._ex["AACPY"] = self.aacpy
        self._ex["CFCMA"] = self.heapa
        self._ex["HEAPA"] = self.heapa
        self._ex["EHEAPA"] = self.heapa
        self._ex["MHINF"] = self.mhinf
        self._ex["MCPCK"] = self.mcpck
        self._ex["NMSEA"] = self.nmsea
        self._ex["PRIMA"] = self.prima
        self._ex["PNRCC"] = self.pnrcc
        self._ex["AGSQR"] = self.no_operation
        self._ex["TKDNA"] = self.tkdna
        self._ex["FLBKA"] = self.no_operation
        self._ex["PNRUA"] = self.pnrua

        # User Defined Executable Macros created for this tool
        self._ex["PARS_DATE"] = self.pars_date
        self._ex["ERROR_CHECK"] = self.error_check
        self._ex["FACE"] = self.face
        self._ex["UIO1_USER_EXIT"] = self.uio1_user_exit
        self._ex["FMSG_USER_EXIT"] = self.fmsg_user_exit
        self._ex["GENERATE_LOCATOR"] = self.generate_locator

        # Realtime Db Macros - Not in ETA5
        self._ex["FINWC"] = self.finwc
        self._ex["FIWHC"] = self.finwc
        # FINHC
        # FILNC, FILEC, FILUC, GETFC, SONIC

        # User defined Db Macros
        self._ex["PDCRE"] = self.no_operation
        self._ex["PDRED"] = self.pdred
        self._ex["PDCLS"] = self.pdcls
        self._ex["PDMOD"] = self.pdmod
        self._ex["PDADD"] = self.no_operation
        self._ex["PDCTL"] = self.pdctl
        # PDDEL

        # TPFDF Macros
        self._ex["DBOPN"] = self.dbopn
        self._ex["DBRED"] = self.dbred
        self._ex["DBCLS"] = self.dbcls
        self._ex["DBIFB"] = self.dbifb
        self._ex["DBADD"] = self.dbadd
        # DBREP, DBMOD, DBDEL

        # No operation
        self._ex["EQU"] = self.no_operation
        self._ex["DS"] = self.no_operation
        self._ex["EXITC"] = self.no_operation

    @property
    def supported_commands(self) -> set:
        return set(self._ex)

    @staticmethod
    def no_operation(node: InstructionType) -> str:
        return node.fall_down
