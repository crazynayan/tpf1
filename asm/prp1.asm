**********************************************************************
*        STUB COPY OF PRP1 TO SAVE PNR ORDINAL/FA INTO WA0PWR
**********************************************************************
         WA0AA REG=R14
         L     R14,CE1CR1
         MVC   WA0PWR,EBCFA5
         MVI   EBER01,0     INDICATE NO ERROR
         BACKC