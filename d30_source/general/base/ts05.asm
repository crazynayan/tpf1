**********************************************************************
*        REGISTER VARIANTS
**********************************************************************
TS050100 DS    0H               VALID FOR REG DATA
         AHI   R15,SUIFF
         BP    TS050110
         AHI   R15,X'00'
TS050110 DS    0H
         LHI   R13,-1
         LHI   R05,X'7FFF'+1
         LHI   RG1,32767
         AHI   R1,#$BCLASS      NO ERROR SINCE C'B' = X'C2'
TS05E100 DS    0H               ERROR FOR REG DATA (INLINE)
*         LHI   RAB,1
*         LHI   R1,X'10000'
*         LHI   R1,65536
TS050200 DS    0H               VALID FOR REG REG FIELD
         STM   R14,R7,656(R9)
         LM    RDA,RGF,CE1DSTMP
TS05E200 DS    0H               ERROR FOR REG REG FIELD (INLINE)
*         STM   R14,R16,EBW000
*         LM    RDC,R7,EBW000
*         LM    R0,R1,PD0_C_ITM
*         STM   R3,R4,4096(R7)
TS050300 DS    0H               VALID FOR REG DATA FIELD
         ICM   R3,B'1001',EBW000
         STCM  R3,B'1111',10(R9)
         ICM   R3,3,=H'-3'
         STCM  R3,B'1000',EBW000
         STCM  R1,0,EBW000      MASK OF 0 IS VALID FOR ICM/STCM
TS05E300 DS    0H               ERROR FOR REG DATA FIELD (INLINE)
*         ICM   R16,1,EBW000
*         STCM  R1,-1,EBW000
*         ICM   R1,16,EBW000
*         ICM   R1,7,-1(R9)
