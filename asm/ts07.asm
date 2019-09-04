**********************************************************************
*        DEFINE CONSTANTS
**********************************************************************
         PGMID 'TS0700'
TS070010 EQU   *
         CLC   EBW000,EBW010
         BNE   TS070020
         LHI   R14,1
TS070020 DS    0F
NAME     DC    C'CLASS'             000
EXAM     DC    2C'NAM'              005
ADR1     DC    A(EXAM)              00c
ADR2     DC    Y(ADR1-EXAM)         010
CHAR1    DC    C'ASDC'              012
CHAR2    DC    CL6'ASDC'
CHAR3    DC    CL2'ASDC'
HEX1     DC    X'E'
HEX2     DC    XL4'FACE'
HEX3     DC    XL1'4243'
BIN1     DC    BL5'0100'
BIN2     DC    BL1'101010'
ZON1     DC    Z'6940'
ZON2     DC    ZL1'-555'
ZON3     DC    ZL5'555'
PCK1     DC    P'1234'
PCK2     DC    PL2'-12345678'
FULL1    DC    F'2000'
FULL2    DC    FL2'100.7'
HALF1    DC    H'2000'
HALF2    DC    H'-2'
FLV      DC    PL2'-29'
FLW      DC    Z'246'
FLX      DC    FL5'-1'
FLY      DC    PL2'4096'
FLZ      DC    ZL2'-29''
FLU      DC    C'-29'
BIG      DC    Y(ADR1-EXAM,L'ADR1-L'EXAM),X'23',YL1(EXAM+ADR1,L'ZON3+L'X
               HALF1-EXAM+#UI2NXT)
         EQU   23