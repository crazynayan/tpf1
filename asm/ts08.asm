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
         L     R1,CE1CR1             8
         LA    R7,EBW040            12
         TM    WA0ET4,#WA0TTY       16
         BO    TS080010             20
         WI0BS REG=R14
         MVC   WI0ARC,$C_AA         24
TS080010 DS    0H                   30
         PUSH  USING
         USING TS08BLK,R14
         USING TS08AWD,R1
         MVC   TS08AAC-TS08REGS(L'TS08AAC,R14),TS08PGR
         MVC   TS08REC,$X_00        36
         LA    R2,PD0_C_ITM         42
         DROP  R1
         WA0AA REG=R1
         WI0BS REG=R14
         OI    WA0ET4,#WA0TTY       46
         MVC   EBW000(2),WI0ARC     50
         BACKC                      56
$C_AA    DC    C'AA'                60
$X_00    DS    0XL256               62
         DC    256X'0'              62