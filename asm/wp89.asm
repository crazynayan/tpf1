CHKAWARD DSECT
ETA9PGMR DS   CL4                  CALLING PROGRAM NAME
ETA90ARC DS   CL2                  AIRLINE CODE
ETA90FNB DS   XL2                  FLIGHT NUMBER.TWO BYTES BINARY
ETA90DTE DS   XL2                  DEPARTURE DATE OF SEGMENT
ETA90BRD DS   CL3                  BOARD POINT
ETA90OFF DS   CL3                  OFF POINT
ETA90SVC DS   CL1                  CLASS OF SERVICE
ETA90MEM DS   CL3                  MEMBERSHIP
ETA90TKT DS   CL1                  TICKET TYPE
ETA90ERR DS   XL1                  ERROR RETURN
$IS$     CSECT
         USING CHKAWARD,R6
         CLC   ETA90FNB,=H'2812'
         BNE   WP890100
         MVI   ETA90TKT,C'A'
WP890100 EQU   *
         MVC   EBW000(L'WP89),WP89
         BACKC
WP89     DC    C'WP89'