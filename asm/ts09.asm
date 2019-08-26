**********************************************************************
*        SUBROUTINE
**********************************************************************
TS090010 EQU   *
         BAS   R4,TS09S100
         JAS   R2,TS09S200
         BACKC
TS09S100 EQU   *
         LTR   R1,R1
         BZR   R4
         AHI   R2,1
         LTR   R1,R1
         NOPR  0
         AHI   R2,1
         BR    R4
TS09S200 DS    0H
         BCR   0,R2
         BCR   15,R2         BR WITH NO FALL DOWN
         BCR   8,R2
         BACKC
TS09E100 EQU   *
         BAS   R16,TS09S100
         BR    -1
