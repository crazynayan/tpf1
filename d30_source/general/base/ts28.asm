* GETFC AND FILE SUPPORT 23-MAY-2022
*
TS280000 EQU   *
         GETFC D2,ID=C'B1',RTP=0,BLOCK=YES
         L     R2,CE1CR2
         MVC   EBW000(4),EBCFA2
         MVI   0(R2),X'B1'
         FILEC D2
         MVC   CE1FA3(2),=C'B1'
         MVC   EBCFA3(4),EBW000
         FIWHC D3,TS28E010
         L     R3,CE1CR3
         MVI   1(R3),X'B2'
         FILUC D3
         GETFC D4,ID=X'C100',RTP=1,BLOCK=NO
         GETCC D4,L4
         L     R4,CE1CR4
         MVC   EBW004(4),EBCFA4
         MVI   0(R4),X'C1'
         FILNC D4
*  SONIC CHECKS
         LHI   R12,1
         SONIC D3
         BNZ   TS280100
         LHI   R12,2
TS280100 EQU   *
         LHI   R14,3
         SONIC (R14)
         JNZ   TS280200
         LHI   R14,4
TS280200 EQU   *
* AAINIT
         WA0AA REG=R1
         L     R1,CE1CR1
         MVI   WA0ET1,1
         AAINT INIT=AAA
         MVI   WA0ET2,2
TS28E010 EQU   *
         EXITC
