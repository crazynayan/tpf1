**********************************************************************
*        WGU4 CALL STUB
**********************************************************************
         PGMID 'TS2401'
         PD0WRK REG=R5
         MI0MI  REG=R6
         GETCC D5,L4
         L     R5,CE1CR5
         PDRED FIELD=NAME,WORKAREA=(LEV,5),NOTFOUND=TS24E010,POINT=YES
         L     R2,PD0_RT_ADR
         L     R6,CE1CR0
         CLC   MI0ACC(6),ZEROES
         BE    TS24E020
         CLC   =C'FF',MI0ACC
         BNE   TS24E020
         ICM   R0,3,MI0ACC+2
         LA    R1,MI0ACC+4
         ENTRC WGU4
TS24EXIT EQU   *
         EXITC
TS24E010 EQU   *
         SENDA MSG='NO NAME IN THE PNR'
TS24E020 EQU   *
         SENDA MSG='INVALID INPUT ENTRY'
ZEROES   DC    10X'0'
