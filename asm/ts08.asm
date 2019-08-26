**********************************************************************
*        DSECT
**********************************************************************
         PGMID 'TS0801'
         WA0AA REG=RG1
         PD0WRK REG=R2
         UI2PF REG=R7
TS08BLK  DSECT
TS08REGS DS    12F
TS08IND  DS    X
#ELIGIND EQU   X'80'
TS08FQ   DS    D
TS08REC  DS    XL256
         ORG   TS08REC
TS08ITM  DS    0XL56
TS08AAC  DS    CL2
TS08FLN  DS    CL4
TS08AWD  DSECT
TS08PGR  DS    CL4
TS08ERR  DS    XL1
$IS$     CSECT
         L     R1,CE1CR1
         LA    R7,EBW040
         TM    WA0ET4,#WA0TTY
         BO    TS080010
         WI0BS REG=R14
         MVC   WI0ARC,$C_AA
TS080010 DS    0H
         PUSH  USING
         USING TS08BLK,R14
         USING TS08AWD,R1
         MVC   TS08AAC-TS08REGS(L'TS08AAC,R14),TS08PGR
         MVC   TS08REC,$X_00
         LA    R2,PD0_C_ITM
         POP   USING
         OI    WA0ET4,#WA0TTY
         MVC   EBW000(2),WI0ARC
         BACKC
$C_AA    DC    C'AA'
$X_00    DS    0XL256
         DC    256X'0'