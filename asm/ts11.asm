**********************************************************************
*        KEY VALUE (REALTIME AND USER DEFINED EXECUTABLE MACROS)
**********************************************************************
TS110010 EQU   *
         WA0AA REG=R1
         AAGET BASEREG=R1,GET=CORE,INIT=YES,FILE=NO
         GETCC D5,L4,FILL=00
         PNRCC ACTION=CRLON,REG=R4
TS110020 EQU   *
         MODEC REG=R14,MODE=31
         GLOBZ REGR=R15
         DETAC D8,CHECK=NO
TS110030 EQU   *
         DBOPN REF=TR1GAA,REG=R4
         DBRED REF=TR1GAA,REG=R4,BEGIN,KEY1=(PKY=#TR1GK40),         @3QX
               KEY2=(R=TR1G_40_OCC,S=$C_AA),                        @3QX
               KEY3=(R=TR1G_40_ACSTIERCODE,S=FQTUUFF),              @3QX
               KEY4=(R=TR1G_40_TIER_EFFD,S=EFFD,C=LE),              @3QX
               KEY5=(R=TR1G_40_TIER_DISD,S=EFFD,C=GE),              @3QX
               ERRORA=TS110020                                      @3Q
         PDCLS WORKAREA=(LEV,5)    CLOSE OPEN PR001W
TS110040 EQU   *
         ATTAC DA
         RELCC D5
         CRUSA S0=5,S1=E           SET TO GET 1ST NAME ITEM
TS110050 EQU   *
         PDRED FIELD=NAME,         GET 1ST AND NEXT NAME               X
               WORKAREA=(LEV,5),                                       X
               NOTFOUND=TS110060,                                      X
               ERROR=TS110070,                                         X
               FORMATOUT=UNPACKED,                                     X
               SEARCH1=ACT
         SYSRA P1=R,P2=021014
TS110060 SENDA MSG='MAXIMUM NUMBER OF NAMES PER PNR IS 99 - CREATE NEW X
               PNR'
         CFCMA ALLOCATE,SREF=TS11PDWK,REG=R4,SIZE=4096,FILL=00,     @3QX
               ERROR=TS110050                                       @3Q
         SERRC R,19000             BAD AAA CHAIN
TS110070 EQU   *
         DBCLS REF=PD0_DF_REFX,FILE=PR001W CLOSE MEMBER PNR         @3Q
         DBIFB REF=PD0_DF_REF,NEWREF=WPSGPNRF,FILE=PR001W,          @3QX
               ERRORA=TS110060                                      @3Q