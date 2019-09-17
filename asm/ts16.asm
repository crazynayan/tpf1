**********************************************************************
*        EXECUTION OF CONDITION INSTRUCTION
*        INPUTS TO BE PROVIDED BEFORE EXECUTING
*        SCENARIO 1 - R0 = 1 IF EBW000[:4] == EBW004[:4] ELSE 2
*        SCENARIO 2 - R1 = 1 IF EBW008 != 'A' ELSE 2
*        SCENARIO 3
*               3.1 - IF R15 == 0 THEN R2 = 1, R3 = 1
*               3.2 - IF R15 < 0 THEN R2 = 2, R3 = 1
*               3.3 - IF R15 > 0 THEN R2 = 3, R3 = 2
*        SCENARIO 4 - R4 = 1 IF R14 ZERO ELSE 2
*        SCENARIO 6
*               6.1 - IF EBW009.X'11' OFF THEN R5 = 1
*               6.2 - IF EBW009.X'11' ON  THEN R5 = 2
*               6.3 - IF EBW009.X'11' MIXED THEN R5 = 3
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
         LHI   R1,1
         BNE   TS160300
         LHI   R1,2
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
TS160600 DS    0H
         BACKC
