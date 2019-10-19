**********************************************************************
*        REGISTER REGISTER
**********************************************************************
         PGMID 'TS0200'
TS020010 SR    R02,RDA      008
TS020020 LTR   RGA,2        00A
         LR    RGE,R15      00C
         LR    R06,R3       00E
         LR    6,R4         010
         LR    R6,R07       012
         JNZ   TS020040     014
TS020030 AR    4,R04        018
TS020040 DS    0H           01A
         BCTR  R5,0
         BACKC
*        ERROR SCENARIO
* TS02E010 LR    R16,R15    ARE CODED INLINE IN THE TEST CASE
* TS02E020 LR    R1,RBD
