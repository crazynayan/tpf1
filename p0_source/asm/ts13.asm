**********************************************************************
*        EXECUTE
**********************************************************************
TS130020 EQU   *
         MVC   EBW000,EBT000
         EX    R1,*-6
TS130010 EQU   *
         TM    EBW000,0
         EX    R15,*-4
         BNO   TS130040
         EX    R15,TS130030
TS130030 PACK  EBW088(8),4(1,R2)
         EX    R15,TS130040
TS130040 DS    0H
         MVC   EBW000,EBT000
         PNAMC NAMETYPE=ENTER,FIELD=EBX000
         EXITC
TS13E000 EQU   *    ERRORS ARE TESTED INLINE
*         EX    R16,TS130010
*         EX    R15,*-1
*         EX    R15,TS13INVALID
