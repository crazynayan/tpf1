**********************************************************************
*        REGISTER REGISTER
**********************************************************************
         PGMID 'TS0200'
TS020010 SR    R02,RDA
TS020020 LTR   RGA,2
         LR    RGE,R15
         LR    R06,R3
         LR    6,R4
         LR    R6,R07
         JNZ   TS020040
TS020030 AR    4,R04
TS020040 DS    0H
         BCTR  R5,0
         BACKC
*        ERROR SCENARIO
TS02E010 LR    R16,R15
TS02E020 LR    R1,RBD
