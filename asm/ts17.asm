**********************************************************************
*        EXECUTION OF REAL TIME MACROS
**********************************************************************
         GETCC D2,L4,FILL=00
         L     R2,CE1CR2
         MVI   0(R2),C'B'
         DETAC D2,CHECK=NO
         GETCC D2,L1,FILL=00
         L     R3,CE1CR2
         MVI   0(R3),C'C'
         RELCC D2
         CRUSA S0=2
         DETAC D1,CHECK=NO
         AAGET BASEREG=R1,GET=CORE,INIT=YES,FILE=NO
         MVI   0(R1),C'A'
         ATTAC D1
         SYSRA P1=R,P2=021014
         SERRC R,19000
         CFCMA ALLOCATE,SREF=TS17PDWK,REG=R4,SIZE=4096,FILL=00,        X
               ERROR=TS17E010
         MVI   0(R4),C'D'
         LHI   R4,4
         HEAPA LOADADD,REF=TS17PDWK,REG=R4
         MVI   1(R4),C'D'
         HEAPA FREE,SREF=TS17PDWK
         LHI   R5,10
         GETCC D3,L4
         LEVTA LEVEL=3,NOTUSED=TS170100
         LHI   R5,20
         SENDA MSG='MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW X
               PNR'
TS170100 DS    0H
*
*        CONSTANTS
*
TS17PDWK DC    CL8'TS17PDWK'
