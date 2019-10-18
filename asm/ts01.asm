**********************************************************************
*        FIELD BITS
**********************************************************************
         OI    EBW008-EBW000(9),1
         OI    EBW000,X'80'
         OI    23(R9),23
         OI    EBT000+L'CE1DSTMP(R9),CE1SEW+CE1CPS+CE1DTX+CE1SNP
         NI    L'EBW000+3+X'10'-EBW000(9),X'FF'-CE1SEW-CE1CPS
         TM    EBW000,1
         BZ    TS010010
         OI    EBX000,1
TS010010 EQU   *
         OI    EBT000,1
         ENTNC TS02
TS01E000 EQU   *
*  ERROR SCENARIOS FOLLOWS
*         OI    23(2,R9),1
*         OI    EBW000(L'EBW001),1
*         OI    ERROR_FIELD,1
*         PD0WRK
*         OI    PD0_C_ITM,1
         OI    C'A'(R2),1              NO ERROR SINCE C'A' IS X'D5'
*         OI    EBW000,250+250          CANNOT HAVE GREATER THAN 255
*         OI    EBW000,#PD0_FLDEMP      NO ERROR SINCE #PD0_FLDEMP = 03
*         OI    -1(R2),1
*         OI    4096(R2),1
