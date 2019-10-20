**********************************************************************
*        FIELD VARIANTS
**********************************************************************
TS040100 DS    0H               VALID FOR FIELD LEN
         XC    CE1WKA,CE1WKA
         CLC   L'CE1WKA+EBW000+4(CE1FA1-CE1FA0,R9),CE1FA1(R9)
         BNE   TS040110
         MVC   EBW000(L'CE1WKA-1),EBW001
*         CLC   2(2,R2),=C'I/'  TODO Uncomment when Literal ready
*         BE    TS040110
*         CLC   =C'C/',2(R2)
*         BL    TS040110
*         UI2PF REG=R7
*         MVC   UI2INC(3),=AL1(#UI2XUI+#UI2CAN,#UI2NXT,#UI2NXT)
         XC    CE1WKA(#$BCLASS),CE1WKA  NO ERROR SINCE C'B' is X'C2'
TS040110 DS    0H
         MVC   23(L'CE1WKA,R3),26(R4)
TS04E100 DS    0H               ERROR FOR FIELD LEN
*         MVC   23(L'CE1WKA+60,R3),26(R4)
*         OC    EBW000(,R4),EBW000
TS040200 DS    0H               VALID FOR FIELD LEN & FIELD LEN
         PACK  CE1DCT,CE1DET
         UNPK  EBW008-EBW000(L'CE1FA1,R3),10(16,R15)
TS04E200 DS    0H               ERROR FOR FIELD LEN & FIELD LEN
*         PACK  CE1DCT,10(17,R15)
TS040300 DS    0H               VALID FOR FIELD DATA
         CLI   EBW000,#$BCLASS
         BNE   TS040310
         MVI   23(R4),L'CE1WKA
TS040310 DS    0H
TS04E300 DS    0H               ERROR FOR FIELD DATA
*         MVI   EBW000,256
*         MVI   EBW000,C'AB'
