import json

UI2CNN = [
    {
        "number": "000",
        "message": "CK ITIN/PSGR DATA"
    },
    {
        "number": "001",
        "message": "$FORMAT$"
    },
    {
        "number": "002",
        "message": "OK"
    },
    {
        "number": "003",
        "message": "NOT IN TBL"
    },
    {
        "number": "004",
        "message": "SINE IN"
    },
    {
        "number": "005",
        "message": "$SEG NR$"
    },
    {
        "number": "006",
        "message": "$CODE$"
    },
    {
        "number": "007",
        "message": "$FLT$"
    },
    {
        "number": "008",
        "message": "$DTE$"
    },
    {
        "number": "009",
        "message": "$CTY$"
    },
    {
        "number": "010",
        "message": "$AL$"
    },
    {
        "number": "011",
        "message": "$UTP$"
    },
    {
        "number": "012",
        "message": "ENTRY VIA"
    },
    {
        "number": "013",
        "message": "UN TO RTE"
    },
    {
        "number": "014",
        "message": "INIT AAA"
    },
    {
        "number": "015",
        "message": "$IC$"
    },
    {
        "number": "016",
        "message": "RPT"
    },
    {
        "number": "017",
        "message": "CN"
    },
    {
        "number": "018",
        "message": "PRIOR RNP DONE"
    },
    {
        "number": "019",
        "message": "$ITEM NR$"
    },
    {
        "number": "020",
        "message": "$DUTY CODE$"
    },
    {
        "number": "021",
        "message": "$CLASS$"
    },
    {
        "number": "022",
        "message": "$CTY$"
    },
    {
        "number": "023",
        "message": "$CTY$"
    },
    {
        "number": "024",
        "message": "$RP3M$"
    },
    {
        "number": "025",
        "message": "$NR IN PTY$"
    },
    {
        "number": "026",
        "message": "SENT"
    },
    {
        "number": "027",
        "message": "$ND -D/Q$"
    },
    {
        "number": "028",
        "message": "$INVLD$"
    },
    {
        "number": "029",
        "message": "ON Q"
    },
    {
        "number": "030",
        "message": "UTP ON Q"
    },
    {
        "number": "031",
        "message": "FIN OR IG"
    },
    {
        "number": "032",
        "message": "$Q$"
    },
    {
        "number": "033",
        "message": "$IC$"
    },
    {
        "number": "034",
        "message": "UTP ON Q"
    },
    {
        "number": "035",
        "message": "UTP ON Q"
    },
    {
        "number": "036",
        "message": "TTY SENT"
    },
    {
        "number": "037",
        "message": "OFF Q"
    },
    {
        "number": "038",
        "message": "OK ONLY FOR PNR FROM Q"
    },
    {
        "number": "039",
        "message": "ON Q"
    },
    {
        "number": "040",
        "message": "UTP ON Q"
    },
    {
        "number": "041",
        "message": "$NR IN PTY$"
    },
    {
        "number": "042",
        "message": "$LN NR$"
    },
    {
        "number": "043",
        "message": "NO AVAIL"
    },
    {
        "number": "044",
        "message": "$CODE$"
    },
    {
        "number": "045",
        "message": "$NR CARS/ROOMS$"
    },
    {
        "number": "046",
        "message": "CNLD FROM"
    },
    {
        "number": "047",
        "message": "PTY NOW"
    },
    {
        "number": "048",
        "message": "SEG"
    },
    {
        "number": "049",
        "message": "NO TRANS PRESENT"
    },
    {
        "number": "050",
        "message": "NO ITIN"
    },
    {
        "number": "051",
        "message": "$FORMAT$"
    },
    {
        "number": "052",
        "message": "NXT REPLACES"
    },
    {
        "number": "053",
        "message": "$SEG$"
    },
    {
        "number": "054",
        "message": "$MSG TOO LONG$"
    },
    {
        "number": "055",
        "message": "FIN OR IG"
    },
    {
        "number": "056",
        "message": "DONE"
    },
    {
        "number": "057",
        "message": "$DUTY CODE$"
    },
    {
        "number": "058",
        "message": "$FORMAT$"
    },
    {
        "number": "059",
        "message": "*"
    },
    {
        "number": "060",
        "message": "R"
    },
    {
        "number": "061",
        "message": "$DISPATCH OFFICE ONLY $"
    },
    {
        "number": "062",
        "message": "RMVD FROM Q"
    },
    {
        "number": "063",
        "message": "$TIME$"
    },
    {
        "number": "064",
        "message": "DONE"
    },
    {
        "number": "065",
        "message": "$NR$"
    },
    {
        "number": "066",
        "message": "$NR$"
    },
    {
        "number": "067",
        "message": "AAA OK"
    },
    {
        "number": "068",
        "message": "$TA$"
    },
    {
        "number": "069",
        "message": "$Q$"
    },
    {
        "number": "070",
        "message": "DONE"
    },
    {
        "number": "071",
        "message": "Q AT MAX"
    },
    {
        "number": "072",
        "message": "DONE"
    },
    {
        "number": "073",
        "message": "SENT TO CONTROL"
    },
    {
        "number": "074",
        "message": "NO SET DSGNTD"
    },
    {
        "number": "075",
        "message": "OK"
    },
    {
        "number": "076",
        "message": "SENT TO CRAS"
    },
    {
        "number": "077",
        "message": "$DTE$"
    },
    {
        "number": "078",
        "message": "$SVC NOT IN SYS$"
    },
    {
        "number": "079",
        "message": "NO DIRECT/CONN SVC"
    },
    {
        "number": "080",
        "message": "NO TBL"
    },
    {
        "number": "081",
        "message": "ALL OK"
    },
    {
        "number": "082",
        "message": "DUPE"
    },
    {
        "number": "083",
        "message": "SKD CHG IN PROG"
    },
    {
        "number": "084",
        "message": "VP"
    },
    {
        "number": "085",
        "message": "NO NAMES"
    },
    {
        "number": "086",
        "message": "SEE SPVR Q"
    },
    {
        "number": "087",
        "message": "NO PNR IN AAA"
    },
    {
        "number": "088",
        "message": "DONE"
    },
    {
        "number": "089",
        "message": "INVLD FOR PTA PNR"
    },
    {
        "number": "090",
        "message": "$Q$"
    },
    {
        "number": "091",
        "message": "$TIME$"
    },
    {
        "number": "092",
        "message": "NXT FLWS"
    },
    {
        "number": "093",
        "message": "CQT RCRD"
    },
    {
        "number": "094",
        "message": "FILE PREV PNR"
    },
    {
        "number": "095",
        "message": "Q FILE MAINT DONE"
    },
    {
        "number": "096",
        "message": "ND RCVD"
    },
    {
        "number": "097",
        "message": "$MORE THAN 1 C/ENTRY$"
    },
    {
        "number": "098",
        "message": "$NAMES EXCEED 99$"
    },
    {
        "number": "099",
        "message": "$SIMUL CHGS PNR IGD$"
    },
    {
        "number": "100",
        "message": "$INVLD TRANS$"
    },
    {
        "number": "101",
        "message": "$NOT SKD DPTR YET$"
    },
    {
        "number": "102",
        "message": "NO MSGS"
    },
    {
        "number": "103",
        "message": "$UN TO DSPLY$"
    },
    {
        "number": "104",
        "message": "NO PNRS ON Q"
    },
    {
        "number": "105",
        "message": "$UN TO DSPLY$"
    },
    {
        "number": "106",
        "message": "IGD"
    },
    {
        "number": "107",
        "message": "$Q$"
    },
    {
        "number": "108",
        "message": "DONE"
    },
    {
        "number": "109",
        "message": "$ND CTY/OA CODE$"
    },
    {
        "number": "110",
        "message": "$CODE$"
    },
    {
        "number": "111",
        "message": "IGD"
    },
    {
        "number": "112",
        "message": "PCCA OK"
    },
    {
        "number": "113",
        "message": "K SNACK AVBL 1"
    },
    {
        "number": "114",
        "message": "FIN ID"
    },
    {
        "number": "115",
        "message": "PCCA PAUSED"
    },
    {
        "number": "116",
        "message": "$CODE$"
    },
    {
        "number": "117",
        "message": "$NO PNL ON FILE$"
    },
    {
        "number": "118",
        "message": "FLWG NOT DONE"
    },
    {
        "number": "119",
        "message": "$UTL PNR$"
    },
    {
        "number": "120",
        "message": "NO X TAKEN"
    },
    {
        "number": "121",
        "message": "MSG NOT FROM Q"
    },
    {
        "number": "122",
        "message": "$CONTROL FUNCTION$"
    },
    {
        "number": "123",
        "message": "$ESXN NR$"
    },
    {
        "number": "124",
        "message": "$EQUIP$"
    },
    {
        "number": "125",
        "message": "$30 DAY MAX$"
    },
    {
        "number": "126",
        "message": "$FLT$"
    },
    {
        "number": "127",
        "message": "$CK ORIG CTY$"
    },
    {
        "number": "128",
        "message": "$ND KXS ENTRY$"
    },
    {
        "number": "129",
        "message": "DONE XCPT CPR"
    },
    {
        "number": "130",
        "message": "$CLASS$"
    },
    {
        "number": "131",
        "message": "$MEAL$"
    },
    {
        "number": "132",
        "message": "$DTE$"
    },
    {
        "number": "133",
        "message": "$LEGS$"
    },
    {
        "number": "134",
        "message": "$CTY$"
    },
    {
        "number": "135",
        "message": "$DUPE FLT NR$"
    },
    {
        "number": "136",
        "message": "$ND SEAT DATA$"
    },
    {
        "number": "137",
        "message": "CD DAYS"
    },
    {
        "number": "138",
        "message": "$AU$"
    },
    {
        "number": "139",
        "message": "$CC NR$"
    },
    {
        "number": "140",
        "message": "$EXSN EXCEED SYS AVL RCRD$"
    },
    {
        "number": "141",
        "message": "SYS ERR-REENTER"
    },
    {
        "number": "142",
        "message": "ESXN CREATED"
    },
    {
        "number": "143",
        "message": "$CONTROL FUNCTION$"
    },
    {
        "number": "144",
        "message": "$DUTY CODE$"
    },
    {
        "number": "145",
        "message": "DSPLY AND REENTER"
    },
    {
        "number": "146",
        "message": "$CK DATA/CALL SPVR$"
    },
    {
        "number": "147",
        "message": "NO ITEMS IN TABLE"
    },
    {
        "number": "148",
        "message": "PLM OK"
    },
    {
        "number": "149",
        "message": "NO FACTS"
    },
    {
        "number": "150",
        "message": "DSPLY PNR"
    },
    {
        "number": "151",
        "message": "$NOTIF CODE$"
    },
    {
        "number": "152",
        "message": "NO FLIFO REC"
    },
    {
        "number": "153",
        "message": "CN"
    },
    {
        "number": "154",
        "message": "RTN"
    },
    {
        "number": "155",
        "message": "$CTY$"
    },
    {
        "number": "156",
        "message": "AVAIL RECAP DONE"
    },
    {
        "number": "157",
        "message": "$FORMAT$"
    },
    {
        "number": "158",
        "message": "$CK STATUS CODE$"
    },
    {
        "number": "159",
        "message": "$ND *OA SINE$"
    },
    {
        "number": "160",
        "message": "NO MSGS"
    },
    {
        "number": "161",
        "message": "SABRE"
    },
    {
        "number": "162",
        "message": "CN"
    },
    {
        "number": "163",
        "message": "CN"
    },
    {
        "number": "164",
        "message": "$PROGRAMMER FUNCTION"
    },
    {
        "number": "165",
        "message": "FILE MAINT CYCLG"
    },
    {
        "number": "166",
        "message": "$RESTRICTED$"
    },
    {
        "number": "167",
        "message": "$ADDR$"
    },
    {
        "number": "168",
        "message": "CN"
    },
    {
        "number": "169",
        "message": "NO NAMES"
    },
    {
        "number": "170",
        "message": "UAF DEFERRED"
    },
    {
        "number": "171",
        "message": "UAF RESTARTED"
    },
    {
        "number": "172",
        "message": "UTL NAME LIST"
    },
    {
        "number": "173",
        "message": "AS"
    },
    {
        "number": "174",
        "message": "$NOTHING TO SCROLL$"
    },
    {
        "number": "175",
        "message": "$DTE$"
    },
    {
        "number": "176",
        "message": "$FREQ$"
    },
    {
        "number": "177",
        "message": "DONE"
    },
    {
        "number": "178",
        "message": "$ND DSPLY$"
    },
    {
        "number": "179",
        "message": "$END OF SCROLL$"
    },
    {
        "number": "180",
        "message": "$INVLD ROUND ROBIN CTY$"
    },
    {
        "number": "181",
        "message": "C/NAME MUST BE 1ST NAME"
    },
    {
        "number": "182",
        "message": "KM CLOSED OUT"
    },
    {
        "number": "183",
        "message": "$UN TO DETAIL$"
    },
    {
        "number": "184",
        "message": "$LEGS$"
    },
    {
        "number": "185",
        "message": "$MAX IS 30$"
    },
    {
        "number": "186",
        "message": "$MAX IND CREATED$"
    },
    {
        "number": "187",
        "message": "REENTER"
    },
    {
        "number": "188",
        "message": "$MEAL$"
    },
    {
        "number": "189",
        "message": "$FACTS$"
    },
    {
        "number": "190",
        "message": "NON CON STUB FLT/CK P"
    },
    {
        "number": "191",
        "message": "KM-"
    },
    {
        "number": "192",
        "message": "UNABL"
    },
    {
        "number": "193",
        "message": "RPT"
    },
    {
        "number": "194",
        "message": "CN"
    },
    {
        "number": "195",
        "message": "CN"
    },
    {
        "number": "196",
        "message": "SYS ERR/REENTER STUB"
    },
    {
        "number": "197",
        "message": "$MAX CPR CREATED$"
    },
    {
        "number": "198",
        "message": "$22 LEG LIMIT$"
    },
    {
        "number": "199",
        "message": "$CONTROL FUNCTION$"
    },
    {
        "number": "200",
        "message": "SKD CHG IN PROG"
    },
    {
        "number": "201",
        "message": "$NR$"
    },
    {
        "number": "202",
        "message": "STUB CREATED"
    },
    {
        "number": "203",
        "message": "PNR POOL COLLECTOR"
    },
    {
        "number": "204",
        "message": "REENTER"
    },
    {
        "number": "205",
        "message": "CR"
    },
    {
        "number": "206",
        "message": "NO AVAIL"
    },
    {
        "number": "207",
        "message": "$CPR NOT IN SYS$"
    },
    {
        "number": "208",
        "message": "RPT ONCE ONLY"
    },
    {
        "number": "209",
        "message": "FILE MAINT/SC ACTIVE"
    },
    {
        "number": "210",
        "message": "DATA COLLECTION"
    },
    {
        "number": "211",
        "message": "$99 SEGS$"
    },
    {
        "number": "212",
        "message": "INVLD ENTRY FOR MSG SWIT"
    },
    {
        "number": "213",
        "message": "NO PSGR DATA"
    },
    {
        "number": "214",
        "message": "NMS/NR IN PTY"
    },
    {
        "number": "215",
        "message": "$NO WL$"
    },
    {
        "number": "216",
        "message": "EPD IN PROG"
    },
    {
        "number": "217",
        "message": "$ITEM NR$"
    },
    {
        "number": "218",
        "message": "$UN TO RECON$"
    },
    {
        "number": "219",
        "message": "PGM STRTD"
    },
    {
        "number": "220",
        "message": "SC WORKING/REDISPLAY Q"
    },
    {
        "number": "221",
        "message": "$EXCEEDS AVBL RCRD$"
    },
    {
        "number": "222",
        "message": "UTL PRIME PNIG"
    },
    {
        "number": "223",
        "message": "PNIG CHAIN ERR"
    },
    {
        "number": "224",
        "message": "SOME PNIGS SKIPD"
    },
    {
        "number": "225",
        "message": "NO PNID FOR ALPHA GRP A"
    },
    {
        "number": "226",
        "message": "NO IND FOR FLT/DTE WTH PNID"
    },
    {
        "number": "227",
        "message": "MISSING IND PNIDS DONE"
    },
    {
        "number": "228",
        "message": "A ALPH GRP PNID DONE"
    },
    {
        "number": "229",
        "message": "PRIME PNID RETRIEVL ERR"
    },
    {
        "number": "230",
        "message": "PNID RESTORED FROM PNIG"
    },
    {
        "number": "231",
        "message": "CHAIN PNID RETRIEVL"
    },
    {
        "number": "232",
        "message": "CHAIN PNIDS DELETED"
    },
    {
        "number": "233",
        "message": "HARDWARE ERR ON PNID REC"
    },
    {
        "number": "234",
        "message": "UTL ALPHA GRP A PNIG"
    },
    {
        "number": "235",
        "message": "TTY SENT PNR NOT FILED"
    },
    {
        "number": "236",
        "message": "TTY RQST INHIBITED"
    },
    {
        "number": "237",
        "message": "$PNR ADRS$"
    },
    {
        "number": "238",
        "message": "PROG ONLY TO PROGMR"
    },
    {
        "number": "239",
        "message": "END RECON"
    },
    {
        "number": "240",
        "message": "$BDG OR DPTD$"
    },
    {
        "number": "241",
        "message": "NOT AVBL/TRY IN 15 MIN"
    },
    {
        "number": "242",
        "message": "NONE"
    },
    {
        "number": "243",
        "message": "$INVLD FOR HOST FLT$"
    },
    {
        "number": "244",
        "message": "NO DAILY"
    },
    {
        "number": "245",
        "message": "$ND PLM PREV STN$"
    },
    {
        "number": "246",
        "message": "NO RPT"
    },
    {
        "number": "247",
        "message": "NO HIST"
    },
    {
        "number": "248",
        "message": "TKT MANUALLY"
    },
    {
        "number": "249",
        "message": "COR NAME FIELD"
    },
    {
        "number": "250",
        "message": "AUX SVC RQD"
    },
    {
        "number": "251",
        "message": "NO AL SEG"
    },
    {
        "number": "252",
        "message": "TKT TOO LONG"
    },
    {
        "number": "253",
        "message": "NONE AVBL"
    },
    {
        "number": "254",
        "message": "NO MORE"
    },
    {
        "number": "255",
        "message": ""
    },
    {
        "number": "256",
        "message": "$INC DSPLY-CK AVAIL$"
    },
    {
        "number": "257",
        "message": "CHECK OAG"
    },
    {
        "number": "258",
        "message": "OAA COMPLETED"
    },
    {
        "number": "259",
        "message": "$Q TICKETING INHIBITED$"
    },
    {
        "number": "260",
        "message": "$ASSIGN PRINTER$"
    },
    {
        "number": "261",
        "message": "$PRINTER IN USE$"
    },
    {
        "number": "262",
        "message": "$K/L NOT PERMITTED$"
    },
    {
        "number": "263",
        "message": "NO TKTG AGREEMENT"
    },
    {
        "number": "264",
        "message": "NO LCL SVC ON AC"
    },
    {
        "number": "265",
        "message": "NOT DETAILED"
    },
    {
        "number": "266",
        "message": "ET REQUIRED"
    },
    {
        "number": "267",
        "message": "SUPER Y/K NOT EFF SEP 1-2"
    },
    {
        "number": "268",
        "message": "CK-BRD PT"
    },
    {
        "number": "269",
        "message": "CK-OFF PT"
    },
    {
        "number": "270",
        "message": "PROT DEV-RL ENTRY REQD"
    },
    {
        "number": "271",
        "message": "$UTP-VERIFY BY PHONE$"
    },
    {
        "number": "272",
        "message": "$UTP-STRIKE IN PROGRESS$"
    },
    {
        "number": "273",
        "message": "DISP AND REENT IN CORR SEQ"
    },
    {
        "number": "274",
        "message": "$TKT IN PROGRESS$"
    },
    {
        "number": "275",
        "message": "$ CONX SEG $"
    },
    {
        "number": "276",
        "message": "$"
    },
    {
        "number": "277",
        "message": "$RA8S$"
    },
    {
        "number": "278",
        "message": "PROCESSING ERROR DETECTED"
    },
    {
        "number": "279",
        "message": "CANNED MSG 2-023 AVAIL"
    },
    {
        "number": "280",
        "message": "SEE ALSO SJC/OAK"
    },
    {
        "number": "281",
        "message": "$NONE AVAILABLE$"
    },
    {
        "number": "282",
        "message": "$CLASS NOT AVAILABLE$"
    },
    {
        "number": "283",
        "message": "CARRIER REQUESTS YOU SELL"
    },
    {
        "number": "284",
        "message": "JOB PCM1 ENDED"
    },
    {
        "number": "285",
        "message": "JOB PCM1 PAUSING"
    },
    {
        "number": "286",
        "message": "JOB PCM1 ABORTING"
    },
    {
        "number": "287",
        "message": "CANNED MSG 2-031 AVAIL"
    },
    {
        "number": "288",
        "message": "CANNED MSG 2-032 AVAIL"
    },
    {
        "number": "289",
        "message": "CANNED MSG 2-033 AVAIL"
    },
    {
        "number": "290",
        "message": "CANNED MSG 2-034 AVAIL"
    },
    {
        "number": "291",
        "message": "SUPER Y/K NOT EFF SEP 1-2"
    },
    {
        "number": "292",
        "message": "CANNED MSG 2-036 AVAIL"
    },
    {
        "number": "293",
        "message": "CANNED MSG 2-037 AVAIL"
    },
    {
        "number": "294",
        "message": "CANNED MSG 2-038 AVAIL"
    },
    {
        "number": "295",
        "message": "CANNED MSG 2-039 AVAIL"
    },
    {
        "number": "296",
        "message": "CANNED MSG 2-040 AVAIL"
    },
    {
        "number": "297",
        "message": "CANNED MSG 2-041 AVAIL"
    },
    {
        "number": "298",
        "message": "CANNED MSG 2-042 AVAIL"
    },
    {
        "number": "299",
        "message": "CANNED MSG 2-043 AVAIL"
    }
]


def create_canned():
    from config import Config
    with open(f"{Config.SOURCES_ROOT}/macro/ui2pf.txt") as ui2pf:
        ui2_file = ui2pf.readlines()
    ui2_file = [line.strip() for line in ui2_file]
    canned_list = list()
    for index, line in enumerate(ui2_file):
        if not line.startswith("#UI2"):
            continue
        if line[4] not in ("0", "1", "2"):
            continue
        words = line.replace("#", "$").split()
        number = int(line[4:7])
        if number >= 256:
            canned_list.append({"number": f"{number:03}", "message": " ".join(words[3:-1])})
            continue
        next_line = ui2_file[index + 1].strip()[:-3]
        words = next_line.replace("#", "$").split()
        canned_list.append({"number": f"{number:03}", "message": " ".join(words[1:])})
    for message in canned_list:
        print(message)
    with open("canned.json", "w") as canned_file:
        json.dump(canned_list, canned_file, indent=4)
