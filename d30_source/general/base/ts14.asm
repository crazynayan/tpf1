**********************************************************************
*        EXECUTION OF NON CONDITIONAL INSTRUCTION (PART 1)
**********************************************************************
         PGMID 'TS14'
         WA0AA  REG=R1
         L      R1,CE1CR1
         LH     R2,C_AA
         STH    R2,WA0BBR
         LHI    R3,#WA0DT2
         STC    R3,WA0TKK
         LR     R5,R3
         SR     R6,R3
         LR     R7,R3
         AR     R7,R3
         IC     R10,WA0TKK
         LH     R4,=Y(L'SPACES)
         LR     R11,R4
         N      R11,=X'000000FF'
         LR     R12,R11
         BCTR   R12,0
         LA     R13,WA0TKK
         LA     R14,2(R13)
         LA     R15,5
         MVC    EBW000,WA0TKK
         MVI    EBW001,C' '
         MVC    EBW002(5),EBW001
         MVC    EBW008(6),EBW001
         XC     EBW008(6),EBW008
         MVC    EBW016,EBW001
         OC     EBW016,EBW000
         MVC    EBW017,EBW016
         NC     EBW017,EBW001
         OI     WA0TY1,#WA0GEN
         MVI    EBW018,X'FF'
         NI     EBW018,#BITA-#WA0GEN
         LH     R0,=H'2'
         MHI    R0,136
         STM    R0,R15,EBT000
**********************************************************************
*        ALL REGISTERS NEEDS TO BE CHECKED FROM EBX000
**********************************************************************
         LHI    R0,0
         LHI    R1,35
         LHI    R15,10
         DR     R0,R15          R0(EBX000)=5, R1(EBX004)=3
         LHI    R2,6144
         LHI    R3,100
         SRDA   R2,22(R15)      R2(EBX008)=0, R3(EBX012)=6144
         LHI    R4,20
         MHI    R4,5            R4(EBX016)=100
         STM    R0,R15,EBX000
         LM     R0,R15,EBT000
         EXITC
C_AA     DC     C'AA'
SPACES   DS     0XL256
         DC     256C' '