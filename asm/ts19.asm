**********************************************************************
*        PDRED FOR HFAX, FQTU, ITIN WITH START PARAM. PDCLS.
*        PNRCC AND WORKING ON DIFFERENT PNRS
**********************************************************************
         PGMID 'TS1901'
FQTUITEM DSECT
FQTUREC  DS    XL63
PNRCWK   DS    XL(13*4)
         ORG   FQTUREC
FQTUTXT  DS    CL7
FQTUITM  DS    0XL56
FQTUAAC  DS    CL2      AIRLINE CODE
FQTUFLN  DS    CL4
FQTUCLS  DS    CL1
FQTUDTE  DS    CL5      DATE
FQTUCTY3 DS    CL10
FQTUDTM  DS    CL4
FQTUUFF  DS    CL3
FQTUSH1  DS    CL1      C'/' - COMPANION, C'*' - MEMBER
FQTUUCR  DS    CL6      PNR LOCATOR
FQTUNOS  DS    CL1      C'N' OR C' ''
FQTUUPG  DS    CL1      UPGRADE IDENTIFIER C'D' OR C'R'
FQTUFAR  DS    CL1      FARE CLASS EG FIRST CLASS IS C'R'
FQTUCNT1 DS    XL1
FQTU1SP1 DS    CL2
FQTUDDT  DS    XL4
         ORG   FQTUCNT1
FQTUSH2  DS    CL1
FQTUUCM  DS    CL6
FQTUBDT  DS    XL4
FQTUUDT  DS    XL4
FQTU1SP2 DS    XL14
$IS$     CSECT
         USING FQTUITEM,R4
         PD0WRK REG=R5
         PR001W REG=R6
         WI0BS  REG=R7
         PNRCM  REG=R10
         GETCC D5,L4,FILL=00
         L     R5,CE1CR5
TS190010 EQU   *
         PDRED FIELD=HOST_FACTS,WORKAREA=(REG,R5),POINT=YES,           X
               SEARCH1=(START,'SSRFQTU'),SEARCH2=(NEW),                X
               FORMATOUT=UNPACKED,NOTFOUND=TS190100
         L     R4,PD0_RT_ADR
         CLC   FQTUAAC,=C'AA'
         BNE   TS190010
         CLI   FQTUUPG,C'R'
         BNE   TS190010
         CLI   FQTUSH1,C'*'
         BNE   TS190010
         L     R1,FQTUFLN
         MVC   EBW001(L'FQTUDTE),FQTUDTE
         LA    R10,PNRCWK
         XC    PM1WRK,PM1WRK
         MVC   PM1LOC,FQTUUCR
         PNRCC ACTION=CRLON,REG=R10
         MVC   EBCFA5,PM1ORN
         PDCLS WORKAREA=(LEV,D5)
         DETAC D1,CHECK=NO
         AAGET BASEREG=R14,GET=CORE,INIT=YES,FILE=NO
         ENTRC PRP1
         MVI   EBW000,0
         LA    R6,EBW000
         LA    R7,EBW001
         ENTRC UCDR
         LTR   R6,R6
         BZ    TS190100
         STH   R6,EBW008
         LA    R7,4(R6)
         MVI   EBW000,X'FF'
         LA    R6,EBW000
         ENTRC UCDR
TS190020 EQU   *
         PDRED FIELD=FQTV,WORKAREA=(LEV,5),FORMATOUT=PACKED,           X
               NOTFOUND=TS190100
         L     R6,PD0_RT_ADR
         CLC   PR00_60_FQT_CXR,$C_AA
         BNE   TS190020
         TM    PR00_60_FQT_TYP,X'40'
         BNO   TS190020
         L     R2,PR00_60_FQT_FTN+3
         PDCLS WORKAREA=(LEV,D5)
         RELCC D1
         ATTAC D1
TS190030 EQU   *
         PDRED FIELD=ITINERARY,WORKAREA=(REG,R5),FORMATOUT=UNPACKED,   X
               NOTFOUND=TS190100
         L     R7,PD0_RT_ADR
         CLC   WI0ARC,$C_AA
         BNE   TS190030
         CLC   WI0FNB,=H'2812'
         BNE   TS190030
         CLC   WI0DTE,EBW008
         BNE   TS190030
         CLC   WI0BRD,=C'DFW'
         BNE   TS190030
         ICM   R3,7,WI0OFF
TS190100 EQU   *
         EXITC
$C_AA    DC    C'AA'
