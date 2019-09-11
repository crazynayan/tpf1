**********************************************************************
*        EXECUTION OF RR AND RX INSTRUCTION
**********************************************************************
         PGMID 'TS14'
         WA0AA  REG=R1
         L      R1,CE1CR1
         LH     R2,C_AA
         STH    R2,WA0BBR
         LHI    R3,#WA0DT2
         STC    R3,WA0TKK
         LH     R4,=Y(L'SPACES)
         N      R4,=X'000000FF'
         BACKC
C_AA     DC     C'AA'
SPACES   DS     0XL256
         DC     256C' '