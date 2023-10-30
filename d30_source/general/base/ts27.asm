*
*  TEST SUPPORT FOR NEW GLOBAL DEFINITION
*  DATE: 11-JAN-22
*  SETUP @FLIFO2,@SHPDD,@@SWITCH AS GLOBAL FIELD
*  SETUP @MH00F AS GLOBAL RECORD
*  INDICATE EBW000='L' FOR LISTING OTHERWISE ASSEMBLER (GLOBZ)
*
TS270000 EQU   *
         CLI   EBW000,C'L'       CALLED FOR LST?
         BE    TS271000          YES - GO THERE
TS270100 EQU   *                 ASSEMBLER GLOBALS
         GLOBZ REGR=R14
         MVC   EBW010,@FLIFO2
         GLOBZ REGS=R14
         MVC   EBW020,@SHPDD
         L     R1,@MH00F         BASE GLOBAL RECORD
         MVC   EBW040,0(R1)      ENSURE NO EXECUTION ERROR
         GLOBZ REGC=R14
         MVC   EBW030,@@SWITCH
         B     TS27E000
TS271000 EQU   *                 LISTING GLOBALS
         USING GLOBAS,R14
         L     R14,CE1GLA
         MVC   EBW010,@FLIFO2
         USING GLOBYS,R14
         L     R14,CE1GLY
         MVC   EBW020,@SHPDD
         L     R1,@MH00F         BASE GLOBAL RECORD
         MVC   EBW040,0(R1)      ENSURE NO EXECUTION ERROR
         USING GLOBAS,R14
         L     R14,CE1GLA
         L     R14,@GBSBC-@GLOBAS(,R14)
         USING GL0BS,R14
         MVC   EBW030,@@SWITCH
TS27E000 EQU   *                 EXIT
         EXITC
