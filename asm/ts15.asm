**********************************************************************
*        EXECUTION OF NON CONDITIONAL INSTRUCTION (PART 2)
**********************************************************************
         PGMID 'TS15'
TS15WK   DSECT
SUM      DS    CL6          EBW032      40
DWD1     DS    FD           EBW040      48
DWD2     DS    FD           EBW048      56
DWD3     DS    FD           EBW056      64
FIN      DS    CL6          EBW064      72
$IS$     CSECT
         USING TS15WK,R14
         LA    R11,TS15MVI
         LA    R12,3
         BCTR  R12,R11
         LA    R12,100
TS15MVI  MVI   EBW001,23
         ICM   R2,B'0011',EBW000
         ST    R2,EBW000
         AHI   R3,-2
         STCM  R3,B'1000',EBW004
         MVC   EBW008(12),SPACES
         MVC   EBW012,C_AA
         MVC   EBW017,C_AA
         LM    R15,R1,EBW008
         STM   R15,R1,EBW020
         LA    R14,EBW032               USE FROM EBW032 UP TO EBW070
         PACK  DWD1,NUM1
         CVB   R4,DWD1
         PACK  DWD2,NUM2
         CVB   R5,DWD2
         LR    R6,R4
         AR    R6,R5
         CVD   R6,DWD3
         UNPK  SUM,DWD3
         MVC   FIN,SUM
         OI    FIN+L'FIN-1,X'F0'
TS15IDX  LA    R7,4
         B     TS15SKIP(R7)
TS15SKIP LA    R7,8
TS15EXIT EXITC
C_AA     DC     C'AA'
SPACES   DS     0XL256
         DC     256C' '
NUM1     DC     CL5'02048'
NUM2     DC     CL5'12048'