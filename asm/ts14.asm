**********************************************************************
*        EXECUTION OF RR AND RX INSTRUCTION
**********************************************************************
         PGMID 'TS14'
         WA0AA  REG=R1
         L      R1,CE1CR1
         LH     R2,C_AA
         N      R2,=X'0000FFFF'
         STH    R2,WA0BBR
         LHI    R3,#WA0DT2
         STC    R3,WA0TKK
         BACKC
C_AA     DC     C'AA'