         BEGIN NAME=TOX1,VERSION=00,BASELESS=YES
         TOXDI REG=R1
         CLC   TOX0ED(4),=C'BOM1'
         JNE   TOX12000
         MVC   TOX0RO,=X'006F2F'
         J     TOX1B000
TOX12000 EQU   *
         CLC   TOX0ED(4),=C'BOM2'
         JNE   TOX12010
         MVC   TOX0RO,=X'006F2E'
         J     TOX1B000
TOX12010 EQU   *
         CLC   TOX0ED(4),=C'BOM3'
         JNE   TOX12020
         MVC   TOX0RO,=X'00017F'
         J     TOX1B000
TOX12020 EQU   *
TOX1B000 BACKC
         FINIS
         END