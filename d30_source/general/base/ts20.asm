**********************************************************************
*        TPFDF
*        25-MAY-2022 DBDEL AND TV OF EBX000:
*        1: DBRED and DBDEL
*        2: DBDEL ALL
*        3: DBDEL ALL
*        4: DBMOD
**********************************************************************
         PGMID 'TS2001'
WORKAREA DSECT
FQTUUFF  DS   CL3
TIER     DS   XL1
$IS$     CSECT
         USING WORKAREA,R5
         TR1GAA REG=R4
         CLI   EBX000,2
         BE    TS201000
         CLI   EBX000,3
         BE    TS202000
         CLI   EBX000,4
         BE    TS203000
         GETCC D2,L4
         L     R5,CE1CR2
         MVC   FQTUUFF,=C'GLD'
* TEST DBOPN, DBRED, DBDEL, DBCLS
         DBOPN REF=TR1GAA,REG=R4
         DBRED REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40),            X
               KEY2=(R=TR1G_40_OCC,S=$C_AA),                           X
               KEY3=(R=TR1G_40_ACSTIERCODE,S=FQTUUFF),                 X
               KEY4=(R=TR1G_40_TIER_EFFD,S=EFFD,C=LE),                 X
               KEY5=(R=TR1G_40_TIER_DISD,S=EFFD,C=GE),                 X
               ERRORA=TS200100
         CLI   SW00RTN,#TPFDBOK
         BNE   TS200100
         MVC   TIER,TR1G_40_PTI
         MVC   EBW000,TIER
         DBDEL REF=TR1GAA,REG=R4,ERROR=TS200100
         DBCLS REF=TR1GAA
* TEST DBDEL WITH KEY
         MVC   FQTUUFF,=C'KEY'
         DBOPN REF=TR1GAA,REG=R4
         DBDEL REF=TR1GAA,REG=R4,KEY1=(PKY=#TR1GK40),                  X
               KEY2=(R=TR1G_40_OCC,S=$C_AA),                           X
               KEY3=(R=TR1G_40_ACSTIERCODE,S=FQTUUFF),                 X
               ERRORA=TS200100
         DBCLS REF=TR1GAA
*  CHECK DBIFB
         DBIFB REF=TR1GAA
         LTR   R3,R3
         BNZ   TS200100
         LHI   R3,1
         DBIFB REF=WPSGPNRF,NEWREF=PD0_DF_REF,FILE=PR001W
         LTR   R3,R3
         BZ    TS200100
         LHI   R0,21
TS200100 EQU   *
         DBCLS REF=PD0_DF_REFX,FILE=PR001W
         EXITC
TS201000 EQU   *
         DBOPN REF=TR1GAA,REG=R4
         DBDEL REF=TR1GAA,REG=R4,ALL,KEY1=(PKY=#TR1GK40),              X
               KEY2=(R=TR1G_40_OCC,S=$C_AA),                           X
               KEY4=(R=TR1G_40_TIER_EFFD,S=EFFD,C=LE),                 X
               KEY5=(R=TR1G_40_TIER_DISD,S=EFFD,C=GE)
         DBCLS REF=TR1GAA
         EXITC
TS202000 EQU   *
         DBOPN REF=TR1GAA,REG=R4
         DBDEL REF=TR1GAA,REG=R4,ALL
         DBCLS REF=TR1GAA
         EXITC
TS203000 EQU   *
         DBOPN REF=TR1GAA,REG=R4
         DBRED REF=TR1GAA,REG=R4,KEY1=(PKY=#TR1GK40),                  X
               KEY2=(R=TR1G_40_OCC,S=$C_AA),                           X
               KEY3=(R=TR1G_40_ACSTIERCODE,S=GOLD),                    X
               ERRORA=TS200100
         MVC   TR1G_40_ACSTIERCODE,=C'AAA'
         DBMOD REF=TR1GAA
         DBCLS REF=TR1GAA
         EXITC
$C_AA    DC    C'AA'
EFFD     DC    X'4CC1'
GOLD     DC    C'GLD'