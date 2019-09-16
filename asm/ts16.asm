**********************************************************************
*        EXECUTION OF CONDITION INSTRUCTION
*        INPUTS TO BE PROVIDED BEFORE EXECUTING
*        SCENARIO 1 - R0 = 1 IF EBW000[:4] == EBW004[:4] ELSE 2
*        SCENARIO 2 - R1 = 1 IF EBW008 != 'A' ELSE 2
*        SCENARIO 3
*               3.1 - IF R7 == 0 THEN R2 = 1, R3 = 1
*               3.2 - IF R7 < 0 THEN R2 = 2, R3 = 1
*               3.3 - IF R7 > 0 THEN R2 = 3, R3 = 2
**********************************************************************
         PGMID 'TS15'
*
*        SCENARIO 1
*
TS150100 DS    0H
         LHI   R0,1
         CLC   EBW000(4),EBW004
         BE    TS150200
         LHI   R0,2
*
*        SCENARIO 2
*
TS150200 DS    0H
         CLI   EBW008,C'A'
         LHI   R1,1
         BNE   TS150300
         LHI   R1,2
*
*        SCENARIO 3
*
TS150300 DS    0H
         CH    R7,=H'0'
         LA    R2,1
         LA    R3,1
         BE    TS150400
         LA    R2,2
         BL    TS150400
         LA    R2,3
         LA    R3,2
TS150400 DS    0H
         BACKC

