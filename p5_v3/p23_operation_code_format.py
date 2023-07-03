from typing import Set

from p5_v3.p01_errors import ParserError
from p5_v3.p22_format import TermFormat, GenericFormat, EquFormat, ExpressionFormat, AssemblerDirectiveNoOperandFormat, MacroCallFormat, \
    RRFormat, SS1Format, \
    SS2Format, SS3Format, RSLFormat, SIFormat, SFormat, SILFormat, RXYFormat, RXFormat, RIL1Format, RS1Format, RI1Format, RS2Format, \
    RSIFormat, RI2Format, RXMnemonicFormat, RI2MnemonicFormat, MacroCallNoOperandFormat, OrgFormat, DsectFormat, CsectFormat


class OperationCodeFormat:
    # Assembler Directive
    DS = TermFormat
    DC = TermFormat
    EQU = EquFormat
    ORG = OrgFormat
    DSECT = DsectFormat
    CSECT = CsectFormat
    USING = ExpressionFormat
    DROP = ExpressionFormat
    PUSH = ExpressionFormat
    POP = ExpressionFormat
    SPACE = ExpressionFormat
    EJECT = AssemblerDirectiveNoOperandFormat
    PRINT = AssemblerDirectiveNoOperandFormat
    BEGIN = MacroCallFormat
    LTORG = AssemblerDirectiveNoOperandFormat
    FINIS = AssemblerDirectiveNoOperandFormat
    END = AssemblerDirectiveNoOperandFormat
    MACRO = AssemblerDirectiveNoOperandFormat
    AIF = AssemblerDirectiveNoOperandFormat
    AGO = AssemblerDirectiveNoOperandFormat
    ANOP = AssemblerDirectiveNoOperandFormat
    ACTR = AssemblerDirectiveNoOperandFormat
    SETA = AssemblerDirectiveNoOperandFormat
    SETB = AssemblerDirectiveNoOperandFormat
    SETC = AssemblerDirectiveNoOperandFormat
    GBLA = AssemblerDirectiveNoOperandFormat
    GBLB = AssemblerDirectiveNoOperandFormat
    GBLC = AssemblerDirectiveNoOperandFormat
    LCLA = AssemblerDirectiveNoOperandFormat
    LCLB = AssemblerDirectiveNoOperandFormat
    # Machine Instruction
    BCTR = RRFormat
    BR = RRFormat
    LR = RRFormat
    LTR = RRFormat
    AR = RRFormat
    SR = RRFormat
    BER = RRFormat
    BNER = RRFormat
    BHR = RRFormat
    BNHR = RRFormat
    BLR = RRFormat
    BNLR = RRFormat
    BMR = RRFormat
    BPR = RRFormat
    BNPR = RRFormat
    BCR = RRFormat
    BOR = RRFormat
    BNOR = RRFormat
    BZR = RRFormat
    BNZR = RRFormat
    NOPR = RRFormat
    LPR = RRFormat
    LNR = RRFormat
    LCR = RRFormat
    MR = RRFormat
    DR = RRFormat
    MVCL = RRFormat
    BASR = RRFormat
    CR = RRFormat
    CLR = RRFormat
    CLCL = RRFormat
    ALR = RRFormat
    SLR = RRFormat
    NR = RRFormat
    OR = RRFormat
    XR = RRFormat
    OC = SS1Format
    XC = SS1Format
    NC = SS1Format
    CLC = SS1Format
    UNPK = SS2Format
    PACK = SS2Format
    MVC = SS1Format
    MVZ = SS1Format
    MVN = SS1Format
    MVO = SS2Format
    ZAP = SS2Format
    AP = SS2Format
    SP = SS2Format
    MP = SS2Format
    CP = SS2Format
    TP = RSLFormat
    SRP = SS3Format
    TR = SS1Format
    TRT = SS1Format
    ED = SS1Format
    EDMK = SS1Format
    OI = SIFormat
    NI = SIFormat
    XI = SIFormat
    TM = SIFormat
    STCK = SFormat
    CLI = SIFormat
    CLHHSI = SILFormat
    MVI = SIFormat
    MVHHI = SILFormat
    LG = RXYFormat
    L = RXFormat
    LH = RXFormat
    LA = RXFormat
    LARL = RIL1Format
    IC = RXFormat
    LLC = RXYFormat
    STH = RXFormat
    N = RXFormat
    O = RXFormat
    X = RXFormat
    ST = RXFormat
    STG = RXFormat
    STC = RXFormat
    CVB = RXFormat
    CVD = RXFormat
    CH = RXFormat
    C = RXFormat
    CL = RXFormat
    A = RXFormat
    AH = RXFormat
    AL = RXFormat
    S = RXFormat
    SH = RXFormat
    SL = RXFormat
    MH = RXFormat
    M = RXFormat
    D = RXFormat
    SLA = RS1Format
    SRA = RS1Format
    SLDA = RS1Format
    SRDA = RS1Format
    SLL = RS1Format
    SRL = RS1Format
    SLDL = RS1Format
    SRDL = RS1Format
    AFI = RIL1Format
    AHI = RI1Format
    LHI = RI1Format
    CHI = RI1Format
    MHI = RI1Format
    LM = RS1Format
    STM = RS1Format
    ICM = RS2Format
    STCM = RS2Format
    CLM = RS2Format
    BAL = RXFormat
    BAS = RXFormat
    JAS = RI1Format
    BRAS = RI1Format
    BCT = RXFormat
    JCT = RI1Format
    BRCT = RI1Format
    BXH = RS1Format
    JXH = RSIFormat
    BRXH = RSIFormat
    BXLE = RS1Format
    JXLE = RSIFormat
    BRXLE = RSIFormat
    EX = RXFormat
    BC = RXFormat
    JC = RI2Format
    BRC = RI2Format
    B = RXMnemonicFormat
    J = RI2MnemonicFormat
    BRU = RI2MnemonicFormat
    NOP = RXMnemonicFormat
    JNOP = RI2MnemonicFormat
    BH = RXMnemonicFormat
    JH = RI2MnemonicFormat
    BRH = RI2MnemonicFormat
    BL = RXMnemonicFormat
    JL = RI2MnemonicFormat
    BRL = RI2MnemonicFormat
    BE = RXMnemonicFormat
    JE = RI2MnemonicFormat
    BRE = RI2MnemonicFormat
    BNH = RXMnemonicFormat
    JNH = RI2MnemonicFormat
    BRNH = RI2MnemonicFormat
    BNL = RXMnemonicFormat
    JNL = RI2MnemonicFormat
    BRNL = RI2MnemonicFormat
    BNE = RXMnemonicFormat
    JNE = RI2MnemonicFormat
    BRNE = RI2MnemonicFormat
    BP = RXMnemonicFormat
    JP = RI2MnemonicFormat
    BRP = RI2MnemonicFormat
    BM = RXMnemonicFormat
    JM = RI2MnemonicFormat
    BRM = RI2MnemonicFormat
    BZ = RXMnemonicFormat
    JZ = RI2MnemonicFormat
    BRZ = RI2MnemonicFormat
    BO = RXMnemonicFormat
    JO = RI2MnemonicFormat
    BRO = RI2MnemonicFormat
    BNP = RXMnemonicFormat
    JNP = RI2MnemonicFormat
    BRNP = RI2MnemonicFormat
    BNM = RXMnemonicFormat
    JNM = RI2MnemonicFormat
    BRNM = RI2MnemonicFormat
    BNZ = RXMnemonicFormat
    JNZ = RI2MnemonicFormat
    BRNZ = RI2MnemonicFormat
    BNO = RXMnemonicFormat
    JNO = RI2MnemonicFormat
    BRNO = RI2MnemonicFormat
    # Realtime macros
    GETCC = MacroCallFormat
    LEVTA = MacroCallFormat
    MODEC = MacroCallFormat
    DETAC = MacroCallFormat
    ATTAC = MacroCallFormat
    RELCC = MacroCallFormat
    RCUNC = MacroCallFormat
    RELFC = MacroCallFormat
    RLCHA = MacroCallFormat
    CRUSA = MacroCallFormat
    SENDA = MacroCallFormat
    SYSRA = MacroCallFormat
    SERRC = MacroCallFormat
    SNAPC = MacroCallFormat
    ENTRC = MacroCallFormat
    ENTNC = MacroCallFormat
    ENTDC = MacroCallFormat
    BACKC = MacroCallNoOperandFormat
    ALASC = MacroCallFormat
    PNAMC = MacroCallFormat
    FLIPC = MacroCallFormat
    EOWNRC = MacroCallFormat
    CREMC = MacroCallFormat
    CREDC = MacroCallFormat
    CREEC = MacroCallFormat
    SWISC = MacroCallFormat
    POSTC = MacroCallFormat
    EVNTC = MacroCallFormat
    EVNQC = MacroCallFormat
    EVNWC = MacroCallFormat
    GLMOD = MacroCallFormat
    FILKW = MacroCallFormat
    KEYCC = MacroCallFormat
    KEYRC = MacroCallFormat
    GLBLC = MacroCallFormat
    DLAYC = MacroCallNoOperandFormat
    DEFRC = MacroCallNoOperandFormat
    REALTIMA = MacroCallFormat
    MALOC = MacroCallFormat
    CALOC = MacroCallFormat
    FREEC = MacroCallFormat
    CINFC = MacroCallFormat
    WTOPC = MacroCallFormat
    FINWC = MacroCallFormat
    FIWHC = MacroCallFormat
    FINHC = MacroCallFormat
    SONIC = MacroCallFormat
    GETFC = MacroCallFormat
    FILUC = MacroCallFormat
    FILEC = MacroCallFormat
    FILNC = MacroCallFormat
    WAITC = MacroCallFormat
    UNFRC = MacroCallFormat
    DBOPN = MacroCallFormat
    DBRED = MacroCallFormat
    DBCLS = MacroCallFormat
    DBIFB = MacroCallFormat
    DBADD = MacroCallFormat
    DBDEL = MacroCallFormat
    DBMOD = MacroCallFormat
    DBREP = MacroCallFormat
    EXITC = MacroCallNoOperandFormat


def get_base_operation_format(operation_code: str) -> GenericFormat:
    try:
        return getattr(OperationCodeFormat, operation_code)
    except AttributeError:
        raise ParserError


def get_operation_format(operation_code: str) -> GenericFormat:
    return get_base_operation_format(operation_code)


def get_base_operation_codes() -> Set[str]:
    return {field for field, _ in dict(OperationCodeFormat.__dict__).items()
            if not field.startswith("_")}


def get_operation_codes() -> Set[str]:
    return get_base_operation_codes()


def is_valid_operation_code(operation_code: str) -> bool:
    return operation_code in get_operation_codes()
