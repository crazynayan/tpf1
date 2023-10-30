**********************************************************************
*        OTHER INSTRUCTION
**********************************************************************
*        DSECT AREA
TS12WRK1 DSECT
         ORG   X'90'
FNAME    DS    CL8
         ORG   FNAME
HWD      DS    H
         ORG   X'1C4'
FWD      DS    F
         ORG   X'500'
FLD1     DS    CL5
FLD2     DS    CL5
         ORG   X'3CC'
TEST     DS    XL1
WORK     DS    F
$IS$     CSECT
**********************************************************************
*        CONSTANTS
FWDA     DC    F'60'            000
HWDA     DC    X'D0123456'      004
ONE      DC    F'1'             008
NUM      DC    F'-2'            00c
FIELDA   DC    XL3'123456'      010
FIELDB   DC    XL4'778899AD'    013
ZERO     DC    F'0'             018
PCK1     DC    P'56789'         01c
PACKED   DC    P'-93'           01f
P2       DC    P'-39'           021
INPT     DC    X'030006'        023
TABLE    DC    C'ABCDEFGHIJ'    026
SENT     DC    C'HELLO WORLD'   030
FULLTBL  DC    193X'FF',9X'00',7X'FF',9X'00',8X'FF',8X'00',22X'FF' 03b
PATTERN  DC    X'4020206B20206B202020'                             13b
**********************************************************************
*        CODE  STARTS FROM HERE
         ORG  8
TS120100 EQU   *
         USING TS12WRK1,R3
         LH    R1,FNAME(R2)
         LPR   R1,R3
         LNR   R2,R2
         LCR   R2,R1
TS120200 EQU   *
         A     R5,FWDA
         AH    R1,HWD
         USING TS12WRK1,R4
         S     R5,FWD(R15)
         SH    R4,HWDA
         MH    R5,HWDA
         MHI   R5,-2
         M     R4,=F'1'
         MR    R4,R15
         DR    R4,R7
         D     R4,NUM
         SLA   R1,1(R2)
         SRA   R3,12
         SLDA  R2,4
         SRDA  R2,32
TS120300 EQU   *
         MVCL  R2,R6
         MVZ   FLD1,=CL5'ABC'
         MVN   FLD1,FLD1+3
         MVO   FIELDB,FIELDA
         BCT   R3,TS120300
         BXH   R1,R4,TS120100
         BXLE  R2,R6,TS120200
         BASR  R8,R0
TS120400 EQU   *
         CR    R3,R5
         C     R3,FWDA
         CHI   R3,-1
         CL    R3,NUM
         CLR   R3,R4
         CLM   R3,9,FLD1
         CLCL  R2,R6
         SLL   R1,7
         SRL   R4,10(R5)
         SLDL  R2,4
         SRDL  R2,32
         ALR   R5,R15
         BC    3,TS120400
         AL    R5,ONE
         SLR   R1,R3
         BC    4,TS120400
         SL    R5,ZERO
TS120500 EQU   *
         NC    FLD1,FLD1
         NR    R2,R3
         OR    R0,R3
         XR    R1,R1
         O     R2,FWD
         X     R0,FWD
         USING TS12WRK1,R6
         XI    TEST,X'CA'
TS120600 EQU   *
         ZAP   FLD1,FLD1+1(2)
         AP    WORK,PACKED
         SP    WORK,PACKED
         MP    WORK,P2
         DP    WORK,=P'-39'
         CP    =P'0',FLD2
         TP    NUM
         SRP   FLD1,4,0
         TR    INPT,TABLE
         TRT   SENT,FULLTBL
         ED    PATTERN,PCK1
         EDMK  PATTERN,PCK1
