         BEGIN NAME=TSJ1,VERSION=00,BASELESS=YES
         SUBID REG=R1
         CLC   SUB0DE(4),=C'BOM1'
         JNE   SUB12000
         MVC   SUB0OR,=X'006F2F'
         J     SUB1B000
SUB12000 EQU   *
         CLC   SUB0DE(4),=C'BOM2'
         JNE   SUB12010
         MVC   SUB0OR,=X'006F2E'
         J     SUB1B000
SUB12010 EQU   *
         CLC   SUB0DE(4),=C'BOM3'
         JNE   SUB12020
         MVC   SUB0OR,=X'00017F'
         J     SUB1B000
SUB12020 EQU   *
SUB1B000 BACKC
         FINIS
         END