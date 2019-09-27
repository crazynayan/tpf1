         PD0WRK REG=R2
         SR    R0,R0
         XC    EBW015(19),EBW015
         GETCC D5,L4,FILL=00
TS180010 EQU   *
         PDRED FIELD=NAME,WORKAREA=(LEV,5),NOTFOUND=TS180100,          X
               FORMATOUT=UNPACKED
         L     R2,CE1CR5
         LA    R2,PD0_C_ITM
         IC    R0,2(R2)
         N     R0,=A(X'1F')
         AR    R2,R0
         OC    EBW015,EBW015
         BNZ   TS18E010
TS180020 EQU   *
         CLI   2(R2),C'C'
         BNE   TS180030
         PACK  EBW088(8),4(2,R2)
         B     TS180050
TS180030 EQU   *
         CLI   2(R2),C'I'
         BE    TS180050
         TM    3(R2),X'F0'
         BO    TS180040
         PACK  EBW088(8),2(1,R2)
         B     TS180050
TS180040 EQU   *
         PACK  EBW088(8),2(2,R2)
TS180050 EQU   *
         CVB   R15,EBW088
         IC    R0,EBW015
         AR    R0,R15
         STC   R0,EBW015
         L     R2,CE1CR5        COMMENT THIS LINE OUT FOR NOTFOUND
         TM    PD0_RT_ID1,#PD0_RT_LST
         BZ    TS180010
TS180100 EQU   *
         IC    R1,EBW015
         CH    R1,=H'99'
         BH    TS18E020
         EXITC
TS18E010 EQU   *
         CLI   2(R2),C'C'
         BNE   TS180020
         SENDA MSG='MORE THAN 1 C/'
TS18E020 EQU   *
         SENDA MSG='MORE THAN 99 NAMES'
