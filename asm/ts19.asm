         PGMID 'TS1901'
FQTUITEM DSECT
FQTUREC  DS    XL256
         ORG   FQTUREC
FQTUTXT  DS    CL7
FQTUITM  DS    0XL56
FQTUAAC  DS    CL2      AIRLINE CODE
FQTUFLN  DS    CL4
FQTUCLS  DS    CL1
FQTUDTE  DS    CL5
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
TS190100 EQU   *
         EXITC