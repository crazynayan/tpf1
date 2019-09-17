**********************************************************************
*        EXECUTION OF CONDITION INSTRUCTION, SUBROUTINES
*        INPUTS TO BE PROVIDED BEFORE EXECUTING
*        SCENARIO 1 - R0 = 1 IF EBW000[:4] == EBW004[:4] ELSE 2
*        SCENARIO 2 - R1 = 2 IF EBW008 != 'A' ELSE 3
*        SCENARIO 3
*               3.1 - IF R15 == 0 THEN R2 = 1, R3 = 1
*               3.2 - IF R15 < 0 THEN R2 = 2, R3 = 1
*               3.3 - IF R15 > 0 THEN R2 = 3, R3 = 2
*        SCENARIO 4 - R4 = 1 IF R14 ZERO ELSE 2
*        SCENARIO 5
*               5.1 - IF EBW009.X'11' OFF THEN R5 = 1
*               5.2 - IF EBW009.X'11' ON  THEN R5 = 2
*               5.3 - IF EBW009.X'11' MIXED THEN R5 = 3
*        SCENARIO 6 - MULTIPLE NESTED SUBROUTINE
*        SCENARIO 7 - EXECUTE
*               7.1 - MOVE B IN EBW020 BASED ON VALUES OF R1 + 1
*               7.2 - PACK 1234 IN EBW024[:4]
*                   - NO. OF DIGITS FROM LEFT TO USE IS R1 + 1
*               7.3 - EBW015 = 15 IF R1 BITS SET IN EBW014 ELSE 16
*               7.4 - SAVE R1 INTO EBW016 USING MVI
**********************************************************************
         PGMID 'TS16'
*
*        SCENARIO 1
*
TS160100 DS    0H
         LHI   R0,1
         CLC   EBW000(4),EBW004
         BE    TS160200
         LHI   R0,2
*
*        SCENARIO 2
*
TS160200 DS    0H
         CLI   EBW008,C'A'
         LHI   R1,2
         BNE   TS160300
         LHI   R1,3
*
*        SCENARIO 3
*
TS160300 DS    0H
         CH    R15,=H'0'
         LA    R2,1
         LA    R3,1
         BE    TS160400
         LA    R2,2
         BL    TS160400
         LA    R2,3
         LA    R3,2
*
*        SCENARIO 4
*
TS160400 DS    0H
         LTR   R14,R14
         JNZ   TS160410
         LHI   R4,1
         B     TS160500
TS160410 DS    0H
         LHI   R4,2
*
*        SCENARIO 5
*
TS160500 DS    0H
         TM    EBW009,X'11'
         BZ    TS160510
         BO    TS160520
         LHI   R5,3
         J     TS160600
TS160510 DS    0H
         LHI   R5,1
         J     TS160600
TS160520 DS    0H
         LHI   R5,2
*
*        SCENARIO 6
*
TS160600 DS    0H
         BAS   R6,TS161100
         BAS   R6,TS161200
*
*        SCENARIO 7
*
TS160700 DS    0H
         MVC   EBW020(0),BEES
         EX    R1,*-6
         LHI   R7,X'30'
         OR    R7,R1
         EX    R7,TS16EX01
         MVI   EBW014,1
         TM    EBW014,0
         EX    R1,*-4
         BZ    TS160710
         MVI   EBW015,15
         B     TS160720
TS160710 DS    0H
         MVI   EBW015,16
TS160720 DS    0H
         EX    R1,TS16EX02
         BACKC
*
*        SUBROUTINES
*
TS161100 DS    0H
         ST    R6,EBX000
         MVI   EBW010,10
         BAS   R6,TS162100
         BAS   R6,TS162200
         L     R6,EBX000
         BR    R6
TS161200 DS    0H
         MVI   EBW011,11
         BR    R6
TS162100 DS    0H
         MVI   EBW012,12
         BR    R6
TS162200 DS    0H
         MVI   EBW013,13
         BR    R6
*
*        CONSTANTS
*
TS16EX01 PACK  EBW024(0),NUM(0)
TS16EX02 MVI   EBW016,0
BEES     DC    C'BBBB'
NUM      DC    C'1234'
