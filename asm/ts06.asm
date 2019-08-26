**********************************************************************
*        BRANCH CONDITION
**********************************************************************
TS060100 DS    0H
         LTR   R1,R1
         LR    R2,R3
         JNZ   TS060120
         LR    R3,R4
         JP    TS060130
         LR    R5,R6
TS060110 DS    0H
         LTR   R2,R2
         LR    R2,R3
         JC    7,TS060130
         LR    R3,R4
         J     TS060100
TS060120 DS    0H
         LTR   R3,R3
         BC    8,TS060110
         AR    R5,R2
         LR    R2,R4
         BC    2,TS060120
TS060130 DS    0H
         LTR   R4,R4
         BNO   TS060100
         JC    15,TS060120
         LTR   R4,R4
         BNO   TS060100
         BC    15,TS060120
         LR    R3,R5
         BACKC
         B     TS060100
TS060140 DS    0H               ERROR PATHS
         LTR   R4,R4
         BNO   TS060100
         BC    0,TS060130
         LTR   R4,R4
         BNO   TS060100
         NOP   TS060130
         LTR   R4,R4
         BNO   TS060100
         JC    0,TS060130
         LTR   R4,R4
         BNO   TS060100
         JNOP  TS060130
TS06E100 DS    0H               ERROR PATHS
         JC    -1,TS06E100
         BC    12,TS06E100
         B     TS06E100(R14)
         JC    14,TS06E100(-1)
         BNZ   0(R8)
         JE    TS061000
