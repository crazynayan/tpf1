**********************************************************************
*        EXECUTION OF NON CONDITIONAL INSTRUCTION (PART 2)
*        ADD EBX000 = 01 SWITCH TO TEST MORE INSTRUCTIONS 17-JAN-2022
*        ADD EBX000 = 02 SWITCH TO TEST MORE INSTRUCTIONS 12-MAY-2022
**********************************************************************
         BEGIN NAME=TS15,VERSION=T0,BASELESS=YES
TS15WK   DSECT
SUM      DS    CL6          EBW032      40
DWD1     DS    FD           EBW040      48
DWD2     DS    FD           EBW048      56
DWD3     DS    FD           EBW056      64
FIN      DS    CL6          EBW064      72
$IS$     CSECT
         USING TS15WK,R14
         LA    R14,EBW032               USE FROM EBW032 UP TO EBW070
         CLI   EBX000,1                 INPUT IS NEW1 REGISTERS TEST
         BE    TS15NEW1                 YES - GO THERE
         CLI   EBX000,2                 INPUT IS NEW1 REGISTERS TEST
         BE    TS15NEW2                 YES - GO THERE
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
         LARL  R13,NUM1
         MVC   EBT000(4),0(R13)
TS15IDX  LA    R7,4
         B     TS15SKIP(R7)
TS15SKIP LA    R7,8
         B     TS15FINS
*
*  NEW1 SET OF REGISTERS
TS15NEW1 EQU   *
         O     R0,=X'12340000'
         O     R0,=X'00005678'
         TRT   EBW032(6),TABLE
         BM    TS15TRT1
         BP    TS15TRT2
         LHI   R3,0
         B     TS15UFR4
TS15TRT1 LHI   R3,1
         B     TS15UFR4
TS15TRT2 LHI   R3,2
TS15UFR4 EQU   *
         LHI   R4,10
         LHI   R5,27
         LHI   R6,34
         MR    R4,R6     TEST MR
         LHI   R7,-14
         SRA   R7,1      TEST SRA
         STCK  EBW040    TEST STCK
         LCR   R10,R7
         LCR   R11,R10   TEST LCR
         LHI   R12,2     TEST BXH = SET INCREMENT TO 6
TS15BXH  EQU   *
         CHI   R13,6            TEST BXH
         BE    TS15CSI
         AHI   R15,1            TEST BXH
         BXH   R13,R12,TS15BXH
         XR    R15,R15
TS15CSI  EQU   *
         MVI    EBT004,1
         CLHHSI EBW004,C'AA'
         BL     TS15FINS
         MVI    EBT004,2
         B      TS15FINS
*
*  NEW2 SET OF REGISTERS
TS15NEW2 EQU   *
          LHI    R1,1
          LHI    R2,100
          CL     R2,EBW000
          BH     TS15AFI
          LHI    R1,2
TS15AFI   EQU    *
          SR     R2,R2
          AFI    R2,-44000
TS15MVHHI EQU    *
          MVHHI  EBW004,X'0FFE'
TS15LLC   EQU    *
          LHI    R3,-1
          LLC    R3,EBT000
TS15XI    EQU    *
          XI     EBT001,X'FF'
          LLC    R4,EBT001
          LPR    R5,R2
          LNR    R6,R5
          LR     R7,R6
          SLA    R7,4(R0)
          LHI    R14,2          Increment for BXLE
          LHI    R15,10         Comprand for BXLE
TS15BXLE  EQU    *
          AHI    R12,1          Loop counter
          BXLE   R13,R14,TS15BXLE
          B      TS15FINS
*
* EXIT
TS15FINS EXITC
C_AA     DC    C'AA'
SPACES   DS    0XL256
         DC    256C' '
NUM1     DC    CL5'02048'
NUM2     DC    CL5'12048'
TABLE    DC    193X'FF',9X'00',7X'FF',9X'00',8X'FF',8X'00',22X'FF'