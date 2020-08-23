**********************************************************************
*        TPFDF
**********************************************************************
         PGMID 'TS2001'
WORKAREA DSECT
FQTUUFF  DS   CL3
EFFD     DS   XL2
TIER     DS   XL1
$IS$     CSECT
         USING WORKAREA,R5
         TR1GAA REG=R4
         GETCC D2,L4
         L     R5,CE1CR2
         MVC   FQTUUFF,=C'GLD'
         MVC   EFFD,=X'4CC1'
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
         DBCLS REF=TR1GAA
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
$C_AA    DC    C'AA'