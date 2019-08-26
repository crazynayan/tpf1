**********************************************************************
*        REGISTER FIELD INDEX
**********************************************************************
         L     R1,CE1CR1
         LA    R2,2
         IC    R1,3(R3,R4)
         STH   R3,L'CE1CR1
         N     R5,EBW008-EB0EB(R6)
         ST    R2,L'EBW000+2(R6,)
         STC   5,EBT000(0,9)
         CVB   RGC,L'CE1CR1+EBW000(,REB)
         CVD   R06,4095(R00,R00)
         CH    R15,4(R15)
         L     R1,CE1CR1(R3)
         L     R1,12
TS03E010 DS    0H                   ERROR PATHS
         L     R16,EBW000
         LA    R1,2(R1,R3,R4)
         LA    R1,2(ABC,R1)
