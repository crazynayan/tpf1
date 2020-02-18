**********************************************************************
*        EXECUTION OF DECIMAL INSTRUCTION
**********************************************************************
         PGMID 'TS2501'
DECIMAL  DSECT
FLD1     DS    PL3    EBW000
RESULT1  DS    XL1    EBW003
FLD2     DS    XL4    EBW004
DWD      DS    D      EBW008
INPUT    DS    XL4    EBW016
RESULT2  DS    CL1    EBW020
WORK     DS    F      EBW024
RESULT3  DS    F      EBW028
RESULT4  DS    F      EBW032
RESULT5  DS    F      EBW036
RESULT6  DS    F      EBW040
RESULT7  DS    F      EBW044
$IS$     CSECT
         USING DECIMAL,R4
TS250100 EQU    *
         LA     R4,EBW000
         MVC    FLD1,=P'56789'
         ZAP    FLD1,FLD1+1(2)
         MVI    RESULT1,1
         JP     TS250110
         MVI    RESULT1,2
TS250110 EQU    *
         ZAP    FLD2,=P'00'
         ZAP    DWD,=P'53'
TS250200 EQU    *
         TP     INPUT
         MVI    RESULT2,X'F0'
         BZ     TS250300
         MVI    RESULT2,X'F1'
         BM     TS250300
         MVI    RESULT2,X'F2'
         BP     TS250300
         MVI    RESULT2,X'F3'
         BO     TS250300
         MVI    RESULT2,X'FF'
TS250300 EQU    *
         ZAP    WORK,PACKED
         MVC    RESULT3,WORK
         AP     WORK,PACKED
         MVC    RESULT4,WORK
         AP     WORK,P2
         MVC    RESULT5,WORK
         SP     WORK,PACKED
         MVC    RESULT6,WORK
         MP     WORK,P2
         MVC    RESULT7,WORK
         DP     WORK,P2
         EXITC
PACKED   DC     P'-93'
P2       DC     P'-39'

