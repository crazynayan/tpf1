continuation_lines = """
BIG      DC    Y(ADR1-EXAM,L'ADR1-L'EXAM),X'23',YL1(EXAM+ADR1,L'ZON3+L'X
               HALF1-EXAM+#UI2NXT)
*  SOME COMMENTS WITH CONTINUATION                                     X
               THIS IS A COMMENT                                       X
               STILL A COMMENT
         ORG *-2   LOCATION COUNTER IS NOW 5
TEST_ORG EQU  *
         ORG ,   RESET LOCATION COUNTER
TS110060 SENDA MSG='MAXIMUM NUMBER OF NAMES,PER PNR IS 99 - CREATE NEW X
               PNR'
TEST1    DS    Y(LONG_LABEL_TO_FILL_UP_SPACE_IN_THE_LINES_OF_OPERANDS+LX
               'SOME_LABEL) THIS IS A COMMENT '    
         SENDA MSG='RAMMAANAARJUNA''S DINNER IS ALWAYS MADE FIRST, ISN'X
               'T IT?'            
"""

using_lines = """
ABC      DSECT
ABC1     DS    XL1
         CSECT
US_LABEL USING R2+1,ABC
"""

continuation_lines_bug = """
         PNRJR FIELD=DEL_ITMS,    CANCELLED ITEMS?              SMJ0612X
               FORMATOUT=PACKED,                                       X
               WORKAREA=(REG,R7)                                       X
               NOTFOUND=CK_ACTV                                        X
               ERROR=TOYF6000
"""
