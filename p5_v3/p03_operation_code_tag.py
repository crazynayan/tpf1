from typing import Set


class OperationCodeTag:
    # Assembler Directive
    DS = "DS"
    DC = "DC"
    EQU = "EQU"
    ORG = "ORG"
    DSECT = "DSECT"
    CSECT = "CSECT"
    USING = "USING"
    DROP = "DROP"
    PUSH = "PUSH"
    POP = "POP"
    SPACE = "SPACE"
    EJECT = "EJECT"
    PRINT = "PRINT"
    TITLE = "TITLE"
    # Realtime macros
    BEGIN = "BEGIN"
    LTORG = "LTORG"
    FINIS = "FINIS"
    END = "END"
    MACRO = "MACRO"
    MNOTE = "MNOTE"
    MEND = "MEND"
    MEXIT = "MEXIT"
    AIF = "AIF"
    AGO = "AGO"
    ANOP = "ANOP"
    ACTR = "ACTR"
    SETA = "SETA"
    SETB = "SETB"
    SETC = "SETC"
    GBLA = "GBLA"
    GBLB = "GBLB"
    GBLC = "GBLC"
    LCLA = "LCLA"
    LCLB = "LCLB"
    LCLC = "LCLC"
    # Machine Instruction
    SAM64 = "SAM64"
    SAM31 = "SAM31"
    SAM24 = "SAM24"
    BCTR = "BCTR"
    BR = "BR"
    LR = "LR"
    LTR = "LTR"
    LTGR = "LTGR"
    AR = "AR"
    SR = "SR"
    SGR = "SGR"
    BER = "BER"
    BNER = "BNER"
    BHR = "BHR"
    BNHR = "BNHR"
    BLR = "BLR"
    BNLR = "BNLR"
    BMR = "BMR"
    BNMR = "BNMR"
    BPR = "BPR"
    BNPR = "BNPR"
    BCR = "BCR"
    BOR = "BOR"
    BNOR = "BNOR"
    BZR = "BZR"
    BNZR = "BNZR"
    NOPR = "NOPR"
    LPR = "LPR"
    LNR = "LNR"
    LCR = "LCR"
    MR = "MR"
    DR = "DR"
    MVCL = "MVCL"
    BASR = "BASR"
    CR = "CR"
    CLR = "CLR"
    CLCL = "CLCL"
    ALR = "ALR"
    SLR = "SLR"
    NR = "NR"
    OR = "OR"
    XR = "XR"
    OC = "OC"
    XC = "XC"
    NC = "NC"
    CLC = "CLC"
    UNPK = "UNPK"
    PACK = "PACK"
    MVC = "MVC"
    MVZ = "MVZ"
    MVN = "MVN"
    MVO = "MVO"
    ZAP = "ZAP"
    AP = "AP"
    SP = "SP"
    MP = "MP"
    DP = "DP"
    CP = "CP"
    TP = "TP"
    SRP = "SRP"
    TR = "TR"
    TRT = "TRT"
    ED = "ED"
    EDMK = "EDMK"
    OI = "OI"
    NI = "NI"
    XI = "XI"
    TM = "TM"
    STCK = "STCK"
    CLI = "CLI"
    CLHHSI = "CLHHSI"
    MVI = "MVI"
    MVHHI = "MVHHI"
    LG = "LG"
    LLGF = "LLGF"
    L = "L"
    LH = "LH"
    LA = "LA"
    LARL = "LARL"
    IC = "IC"
    LLC = "LLC"
    STH = "STH"
    N = "N"
    O = "O"
    X = "X"
    ST = "ST"
    STG = "STG"
    STC = "STC"
    CVB = "CVB"
    CVD = "CVD"
    CVDG = "CVDG"
    CH = "CH"
    C = "C"
    CL = "CL"
    A = "A"
    AH = "AH"
    AL = "AL"
    S = "S"
    SH = "SH"
    SL = "SL"
    MH = "MH"
    M = "M"
    D = "D"
    DSGF = "DSGF"
    SLA = "SLA"
    SRA = "SRA"
    SLDA = "SLDA"
    SRDA = "SRDA"
    SLL = "SLL"
    SRL = "SRL"
    SRLG = "SRLG"
    SLDL = "SLDL"
    SRDL = "SRDL"
    AFI = "AFI"
    AHI = "AHI"
    AGHI = "AGHI"
    LHI = "LHI"
    LGHI = "LGHI"
    CHI = "CHI"
    MHI = "MHI"
    LM = "LM"
    STM = "STM"
    ICM = "ICM"
    STCM = "STCM"
    CLM = "CLM"
    BAL = "BAL"
    BALR = "BALR"
    BAS = "BAS"
    JAS = "JAS"
    BRAS = "BRAS"
    BCT = "BCT"
    BCTG = "BCTG"
    JCT = "JCT"
    BRCT = "BRCT"
    BXH = "BXH"
    JXH = "JXH"
    BRXH = "BRXH"
    BXLE = "BXLE"
    JXLE = "JXLE"
    BRXLE = "BRXLE"
    EX = "EX"
    EXRL = "EXRL"
    BC = "BC"
    JC = "JC"
    BRC = "BRC"
    B = "B"
    J = "J"
    BRU = "BRU"
    NOP = "NOP"
    JNOP = "JNOP"
    BH = "BH"
    JH = "JH"
    BRH = "BRH"
    BL = "BL"
    JL = "JL"
    BRL = "BRL"
    BE = "BE"
    JE = "JE"
    BRE = "BRE"
    BNH = "BNH"
    JNH = "JNH"
    BRNH = "BRNH"
    BNL = "BNL"
    JNL = "JNL"
    BRNL = "BRNL"
    BNE = "BNE"
    JNE = "JNE"
    BRNE = "BRNE"
    BP = "BP"
    JP = "JP"
    BRP = "BRP"
    BM = "BM"
    JM = "JM"
    BRM = "BRM"
    BZ = "BZ"
    JZ = "JZ"
    BRZ = "BRZ"
    BO = "BO"
    JO = "JO"
    BRO = "BRO"
    BNP = "BNP"
    JNP = "JNP"
    BRNP = "BRNP"
    BNM = "BNM"
    JNM = "JNM"
    BRNM = "BRNM"
    BNZ = "BNZ"
    JNZ = "JNZ"
    BRNZ = "BRNZ"
    BNO = "BNO"
    JNO = "JNO"
    BRNO = "BRNO"
    # Realtime macros
    GETCC = "GETCC"
    LEVTA = "LEVTA"
    MODEC = "MODEC"
    DETAC = "DETAC"
    ATTAC = "ATTAC"
    RELCC = "RELCC"
    RCUNC = "RCUNC"
    RCRFC = "RCRFC"
    RELFC = "RELFC"
    RLCHA = "RLCHA"
    RCHKA = "RCHKA"
    CRUSA = "CRUSA"
    SENDA = "SENDA"
    SYSRA = "SYSRA"
    SERRC = "SERRC"
    SNAPC = "SNAPC"
    ENTRC = "ENTRC"
    ENTNC = "ENTNC"
    ENTDC = "ENTDC"
    BACKC = "BACKC"
    ALASC = "ALASC"
    PNAMC = "PNAMC"
    FLIPC = "FLIPC"
    EOWNRC = "EOWNRC"
    CREMC = "CREMC"
    CREDC = "CREDC"
    CREEC = "CREEC"
    CRETC = "CRETC"
    CREXC = "CREXC"
    SWISC = "SWISC"
    POSTC = "POSTC"
    EVNTC = "EVNTC"
    EVNQC = "EVNQC"
    EVNWC = "EVNWC"
    GLMOD = "GLMOD"
    FILKW = "FILKW"
    KEYCC = "KEYCC"
    KEYRC = "KEYRC"
    GLBLC = "GLBLC"
    DLAYC = "DLAYC"
    DEFRC = "DEFRC"
    REALTIMA = "REALTIMA"
    MALOC = "MALOC"
    CALOC = "CALOC"
    FREEC = "FREEC"
    CINFC = "CINFC"
    WTOPC = "WTOPC"
    FINWC = "FINWC"
    FIWHC = "FIWHC"
    FINHC = "FINHC"
    FINDC = "FINDC"
    SONIC = "SONIC"
    GETFC = "GETFC"
    FILUC = "FILUC"
    FILEC = "FILEC"
    FILNC = "FILNC"
    WAITC = "WAITC"
    UNFRC = "UNFRC"
    EXITC = "EXITC"
    GLOBZ = "GLOBZ"
    GLOBLC = "GLOBLC"
    SYNCC = "SYNCC"
    DECBC = "DECBC"
    LODIC = "LODIC"
    SIPCC = "SIPCC"
    TOUTC = "TOUTC"
    TOURC = "TOURC"
    ALPHA = "ALPHA"
    SREGSC = "SREGSC"
    LREGSC = "LREGSC"
    EDITA = "EDITA"
    MOVEC = "MOVEC"
    GSVAC = "GSVAC"
    # System Macros
    CCIDC = "CCIDC"
    SYSTC = "SYSTC"
    ECBMC = "ECBMC"
    TIMEC = "TIMEC"
    TMSLC = "TMSLC"
    CRATC = "CRATC"
    # TPFDF
    TPFDB = "TPFDB"
    DBOPN = "DBOPN"
    DBRED = "DBRED"
    DBCLS = "DBCLS"
    DBIFB = "DBIFB"
    DBADD = "DBADD"
    DBDEL = "DBDEL"
    DBMOD = "DBMOD"
    DBREP = "DBREP"
    DBRET = "DBRET"
    DBDSP = "DBDSP"
    DBCRE = "DBCRE"
    DBCLR = "DBCLR"
    DBKEY = "DBKEY"
    DBCPY = "DBCPY"
    DBSRT = "DBSRT"
    DBCKP = "DBCKP"
    # SPM
    hashUEXIT = "#UEXIT"
    hashURTRN = "#URTRN"
    hashSPM = "#SPM"
    hashGOTO = "#GOTO"
    hashLOCA = "#LOCA"
    hashPERF = "#PERF"
    hashIF = "#IF"
    hash = "#"
    hashEIF = "#EIF"
    hashELIF = "#ELIF"
    hashELSE = "#ELSE"
    hashDO = "#DO"
    hashEDO = "#EDO"
    hashEXIF = "#EXIF"
    hashOREL = "#OREL"
    hashDOEX = "#DOEX"
    hashELOP = "#ELOP"
    hashSUBR = "#SUBR"
    hashESUB = "#ESUB"
    hashEIFM = "#EIFM"
    hashSTPH = "#STPH"
    hashSTPR = "#STPR"
    hashSTPC = "#STPC"
    hashSTPF = "#STPF"
    hashEXEC = "#EXEC"
    hashCOND = "#COND"
    hashCONB = "#CONB"
    hashCONT = "#CONT"
    hashCONX = "#CONX"
    hashCAST = "#CAST"
    hashCASE = "#CASE"
    hashECAS = "#ECAS"
    # DCL
    DCL = "DCL"
    IF = "IF"
    ENDIF = "ENDIF"

# {d:v for d,v in dict(A.__dict__).items() if not d.startswith("_")}
def get_base_operation_code_tags() -> Set[str]:
    return {op_code for field, op_code in dict(OperationCodeTag.__dict__).items()
            if not field.startswith("_")}

