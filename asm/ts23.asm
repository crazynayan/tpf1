**********************************************************************
*        TEST REALTIME AND USER DEFINED MACROS
*        1) ALASC
*        2) MHINF
*        3) PRIMA
**********************************************************************
         PGMID 'TS2301'
FTNWK    DSECT
         DS    XL16            AUTO STORAGE HEADER
FTNREG   DS    (0*7)F          REGISTER SAVE AREA
FTNRG1   DS    F               SAVE R1
FTNRGA   DS    F               SAVE R2
FTNRGB   DS    F               SAVE R3
FTNRGC   DS    F               SAVE R4
FTNRGD   DS    F               SAVE R5
FTNRGE   DS    F               SAVE R6
FTNRGF   DS    F               SAVE R7
$IS$     CSECT
         USING FTNWK,R4
*
*        1) ALASC
*
TS230100 EQU   *
         LHI   R1,1
         LHI   R2,2
         LHI   R3,3
         LHI   R4,4
         LHI   R5,5
         LHI   R6,6
         LHI   R7,7
         ALASC L2
         STM   R1,R6,8(R7)
         L     R4,CE1AUT
         MVC   FTNRGF,8(R4)
         MVC   EBW000(28),FTNREG
*
*        2) MHINF
*
TS230200 EQU   *
         LA    R10,VX
         MHINF ECB,REG=R10,INPTR=NAME
*
*        3) PRIMA
*
TS230300 EQU   *
         LHI   R11,1
         PRIMA AAA,PH=ANY,NO=TS230400,MODE=CHECK
         AHI   R11,1
         PRIMA AAA,PH=1F,YES=TS230390,MODE=CHECK
         PRIMA AAA,PH=1B,NO=TS230400,MODE=CHECK
         AHI   R11,3
         J     TS230400
TS230390 EQU   *
         AHI   R11,2
TS230400 EQU   *
TS23EXIT EQU   *
         EXITC
VX       DC    C'VX'
