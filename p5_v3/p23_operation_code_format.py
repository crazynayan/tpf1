from typing import Set, Type, List

from p5_v3.p01_errors import ParserError
from p5_v3.p05_domain import ClientDomain
from p5_v3.p22_format import GenericFormat, EquFormat, ExpressionAssemblerDirectiveFormat, NoOperandAssemblerDirectiveFormat, \
    MacroCallFormat, RRFormat, SS1Format, \
    SS2Format, SS3Format, RSLFormat, SIFormat, SFormat, SILFormat, RXYFormat, RXFormat, RIL1Format, RS1Format, RI1Format, RS2Format, \
    RSIFormat, RI2Format, RXMnemonicFormat, RI2MnemonicFormat, NoOperandMacroCallFormat, OrgFormat, DsectFormat, CsectFormat, DSFormat, \
    DCFormat, DataMacroCallFormat, CallSegmentFormat, CretcFormat, SwiscFormat, RIL2Format, EFormat, RREFormat, RSY1Format


class OperationCodeFormat:
    # Assembler Directive
    DS = DSFormat
    DC = DCFormat
    EQU = EquFormat
    ORG = OrgFormat
    DSECT = DsectFormat
    CSECT = CsectFormat
    USING = ExpressionAssemblerDirectiveFormat
    DROP = ExpressionAssemblerDirectiveFormat
    PUSH = ExpressionAssemblerDirectiveFormat
    POP = ExpressionAssemblerDirectiveFormat
    SPACE = ExpressionAssemblerDirectiveFormat
    EJECT = NoOperandAssemblerDirectiveFormat
    PRINT = NoOperandAssemblerDirectiveFormat
    TITLE = NoOperandAssemblerDirectiveFormat
    LTORG = NoOperandAssemblerDirectiveFormat
    END = NoOperandAssemblerDirectiveFormat
    MACRO = NoOperandAssemblerDirectiveFormat
    MEXIT = NoOperandAssemblerDirectiveFormat
    MEND = NoOperandAssemblerDirectiveFormat
    MNOTE = NoOperandAssemblerDirectiveFormat
    AIF = NoOperandAssemblerDirectiveFormat
    AGO = NoOperandAssemblerDirectiveFormat
    ANOP = NoOperandAssemblerDirectiveFormat
    ACTR = NoOperandAssemblerDirectiveFormat
    SETA = NoOperandAssemblerDirectiveFormat
    SETB = NoOperandAssemblerDirectiveFormat
    SETC = NoOperandAssemblerDirectiveFormat
    GBLA = NoOperandAssemblerDirectiveFormat
    GBLB = NoOperandAssemblerDirectiveFormat
    GBLC = NoOperandAssemblerDirectiveFormat
    LCLA = NoOperandAssemblerDirectiveFormat
    LCLB = NoOperandAssemblerDirectiveFormat
    LCLC = NoOperandAssemblerDirectiveFormat
    # Machine Instruction
    BCTR = RRFormat
    BR = RRFormat
    LR = RRFormat
    LTR = RRFormat
    AR = RRFormat
    SR = RRFormat
    SGR = RREFormat
    LTGR = RREFormat
    BER = RRFormat
    BNER = RRFormat
    BHR = RRFormat
    BNHR = RRFormat
    BLR = RRFormat
    BNLR = RRFormat
    BMR = RRFormat
    BNMR = RRFormat
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
    BALR = RRFormat
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
    DP = SS2Format
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
    LLGF = RXYFormat
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
    CVDG = RXYFormat
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
    DSGF = RXYFormat
    SLA = RS1Format
    SRA = RS1Format
    SLDA = RS1Format
    SRDA = RS1Format
    SLL = RS1Format
    SRL = RS1Format
    SRLG = RSY1Format
    SLDL = RS1Format
    SRDL = RS1Format
    AFI = RIL1Format
    AHI = RI1Format
    LHI = RI1Format
    CHI = RI1Format
    MHI = RI1Format
    LGHI = RI1Format
    AGHI = RI1Format
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
    BCTG = RXYFormat
    JCT = RI1Format
    BRCT = RI1Format
    BXH = RS1Format
    JXH = RSIFormat
    BRXH = RSIFormat
    BXLE = RS1Format
    JXLE = RSIFormat
    BRXLE = RSIFormat
    EX = RXFormat
    EXRL = RIL2Format
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
    SAM64 = EFormat
    SAM31 = EFormat
    SAM24 = EFormat
    # Realtime macros
    BEGIN = MacroCallFormat
    FINIS = NoOperandMacroCallFormat
    GETCC = MacroCallFormat
    LEVTA = MacroCallFormat
    MODEC = MacroCallFormat
    DETAC = MacroCallFormat
    ATTAC = MacroCallFormat
    RELCC = MacroCallFormat
    RCUNC = MacroCallFormat
    RCRFC = MacroCallFormat
    RELFC = MacroCallFormat
    RLCHA = NoOperandMacroCallFormat
    RCHKA = NoOperandMacroCallFormat
    CRUSA = MacroCallFormat
    SENDA = MacroCallFormat
    SYSRA = MacroCallFormat
    SERRC = MacroCallFormat
    SNAPC = MacroCallFormat
    ENTRC = CallSegmentFormat
    ENTNC = CallSegmentFormat
    ENTDC = CallSegmentFormat
    BACKC = NoOperandMacroCallFormat
    ALASC = MacroCallFormat
    PNAMC = MacroCallFormat
    FLIPC = MacroCallFormat
    EOWNRC = MacroCallFormat
    CREMC = CallSegmentFormat
    CREDC = CallSegmentFormat
    CREEC = CallSegmentFormat
    CREXC = CallSegmentFormat
    CRETC = CretcFormat
    SWISC = SwiscFormat
    POSTC = MacroCallFormat
    EVNTC = MacroCallFormat
    EVNQC = MacroCallFormat
    EVNWC = MacroCallFormat
    GLMOD = NoOperandMacroCallFormat
    FILKW = MacroCallFormat
    KEYCC = NoOperandMacroCallFormat
    KEYRC = NoOperandMacroCallFormat
    GLBLC = MacroCallFormat
    DLAYC = NoOperandMacroCallFormat
    DEFRC = NoOperandMacroCallFormat
    REALTIMA = MacroCallFormat
    MALOC = MacroCallFormat
    CALOC = MacroCallFormat
    FREEC = MacroCallFormat
    CINFC = MacroCallFormat
    WTOPC = MacroCallFormat
    FINDC = MacroCallFormat
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
    EXITC = NoOperandMacroCallFormat
    GLOBZ = MacroCallFormat
    GLOBLC = MacroCallFormat
    SYNCC = MacroCallFormat
    DECBC = MacroCallFormat
    LODIC = MacroCallFormat
    SIPCC = MacroCallFormat
    TOUTC = MacroCallFormat
    TOURC = MacroCallFormat
    ALPHA = MacroCallFormat
    SREGSC = MacroCallFormat
    LREGSC = MacroCallFormat
    EDITA = MacroCallFormat
    MOVEC = MacroCallFormat
    GSVAC = MacroCallFormat
    # System Macros
    CCIDC = MacroCallFormat
    SYSTC = MacroCallFormat
    ECBMC = MacroCallFormat
    TIMEC = MacroCallFormat
    TMSLC = MacroCallFormat
    CRATC = MacroCallFormat
    # TPFDF
    TPFDB = MacroCallFormat
    DBOPN = MacroCallFormat
    DBRED = MacroCallFormat
    DBCLS = MacroCallFormat
    DBIFB = MacroCallFormat
    DBADD = MacroCallFormat
    DBDEL = MacroCallFormat
    DBMOD = MacroCallFormat
    DBREP = MacroCallFormat
    DBRET = MacroCallFormat
    DBDSP = MacroCallFormat
    DBCRE = MacroCallFormat
    DBCLR = NoOperandMacroCallFormat
    DBKEY = MacroCallFormat
    DBCPY = MacroCallFormat
    DBSRT = MacroCallFormat
    DBCKP = MacroCallFormat
    # SPM
    hashUEXIT = NoOperandAssemblerDirectiveFormat
    hashURTRN = NoOperandAssemblerDirectiveFormat
    hashSPM = NoOperandMacroCallFormat
    hashGOTO = NoOperandMacroCallFormat
    hashLOCA = NoOperandMacroCallFormat
    hashPERF = NoOperandMacroCallFormat
    hashIF = NoOperandMacroCallFormat
    hash = NoOperandMacroCallFormat
    hashEIF = NoOperandMacroCallFormat
    hashELIF = NoOperandMacroCallFormat
    hashELSE = NoOperandMacroCallFormat
    hashDO = NoOperandMacroCallFormat
    hashEDO = NoOperandMacroCallFormat
    hashEXIF = NoOperandMacroCallFormat
    hashOREL = NoOperandMacroCallFormat
    hashDOEX = NoOperandMacroCallFormat
    hashELOP = NoOperandMacroCallFormat
    hashSUBR = NoOperandMacroCallFormat
    hashESUB = NoOperandMacroCallFormat
    hashEIFM = NoOperandMacroCallFormat
    hashSTPH = NoOperandMacroCallFormat
    hashSTPR = NoOperandMacroCallFormat
    hashSTPC = NoOperandMacroCallFormat
    hashSTPF = NoOperandMacroCallFormat
    hashEXEC = MacroCallFormat
    hashCOND = NoOperandMacroCallFormat
    hashCONB = NoOperandMacroCallFormat
    hashCONT = NoOperandMacroCallFormat
    hashCONX = NoOperandMacroCallFormat
    hashCAST = NoOperandMacroCallFormat
    hashCASE = NoOperandMacroCallFormat
    hashECAS = NoOperandMacroCallFormat
    # DCL
    DCL = NoOperandMacroCallFormat
    IF = NoOperandMacroCallFormat
    ENDIF = NoOperandMacroCallFormat


def sanitize_operation_code(operation_code: str) -> str:
    return operation_code.replace("#", "hash")


def desanitize_operation_code(operation_code: str) -> str:
    return operation_code.replace("hash", "#")


def get_operation_format(operation_code: str, domain: ClientDomain) -> Type[GenericFormat]:
    try:
        return getattr(domain.get_user_defined_operation_code_class(), sanitize_operation_code(operation_code))
    except AttributeError:
        if domain.is_macro_valid(operation_code):
            return DataMacroCallFormat
        if operation_code in get_tool_specific_operation_codes():
            return NoOperandMacroCallFormat
        raise ParserError(operation_code)
    except KeyError:
        raise ParserError("Invalid domain")


def get_operation_codes_from_format(operation_code_format: Type[object]) -> Set[str]:
    return {desanitize_operation_code(field) for field, _ in dict(operation_code_format.__dict__).items()
            if not field.startswith("_")}


def get_base_operation_codes() -> Set[str]:
    return get_operation_codes_from_format(OperationCodeFormat)


def get_tool_specific_operation_codes() -> Set[str]:
    return {"FACE"}


def get_operation_codes(domain: ClientDomain) -> Set[str]:
    return get_base_operation_codes() | get_operation_codes_from_format(
        domain.get_user_defined_operation_code_class()) | get_tool_specific_operation_codes()


def is_valid_operation_code(operation_code: str) -> bool:
    return operation_code in get_operation_codes()


def check_operation_code_validity(operation_codes: List[str], domain: ClientDomain) -> List[bool]:
    valid_codes: Set[str] = get_operation_codes(domain) | set(domain.get_macro_list())
    return [operation_code in valid_codes for operation_code in operation_codes]
