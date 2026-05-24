import csv
import json
import socket
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from scanner.engine import HostResult

SERVICE_NAMES: dict[int, str] = {
    # ===== Well-known system ports (0-1023) =====
    # 0 is reserved (IANA), not assigned
    1: "tcpmux", 2: "compressnet", 3: "compressnet", 5: "rje", 7: "echo", 9: "discard",
    11: "systat", 13: "daytime", 15: "netstat", 17: "qotd", 18: "msp", 19: "chargen",
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    27: "nsw-fe", 29: "msg-icp", 31: "msg-auth", 33: "dsp", 37: "time",
    38: "rap", 39: "rlp", 42: "nameserver", 43: "whois", 49: "tacacs",
    50: "re-mail-ck", 51: "la-maint", 52: "xns-time", 53: "domain",
    54: "xns-ch", 55: "isi-gl", 56: "xns-auth", 57: "mtp", 58: "xns-mail",
    59: "priv-file", 61: "ni-mail", 62: "acas", 63: "whoispp", 64: "covia",
    65: "tacacs-ds", 66: "oracle-sql", 67: "dhcp-server", 68: "dhcp-client",
    69: "tftp", 70: "gopher", 71: "netrjs-1", 72: "netrjs-2",
    73: "netrjs-3", 74: "netrjs-4", 76: "deos", 78: "vettcp", 79: "finger",
    80: "http", 81: "hosts2-ns", 82: "xfer", 83: "mit-ml-dev", 84: "ctf",
    85: "mit-ml-dev", 86: "mfcobol", 88: "kerberos", 89: "su-mit-tg",
    90: "dnsix", 91: "mit-dov", 92: "npp", 93: "dcp", 94: "objcall",
    95: "supdup", 96: "dixie", 97: "swift-rvf", 98: "tacnews", 99: "metagram",
    101: "hostname", 102: "iso-tsap", 103: "gppitnp", 104: "acr-nema",
    105: "csnet-ns", 106: "3com-tsmux", 107: "rtelnet", 108: "snagas",
    109: "pop2", 110: "pop3", 111: "rpcbind", 112: "mcidas",
    113: "ident", 115: "sftp", 116: "ansanotify", 117: "uucp-path",
    118: "sqlserv", 119: "nntp", 120: "cfdptkt", 121: "erpc",
    122: "smakynet", 123: "ntp", 124: "ansatrader", 125: "locus-map",
    126: "nxedit", 127: "locus-con", 128: "gss-xlicen", 129: "pwdgen",
    130: "cisco-fna", 131: "cisco-tna", 132: "cisco-sys", 133: "statsrv",
    134: "ingres-net", 135: "msrpc", 136: "profile", 137: "netbios-ns",
    138: "netbios-dgm", 139: "netbios-ssn", 140: "emfis-data",
    141: "emfis-cntl", 142: "bl-idm", 143: "imap", 144: "uma",
    145: "uaac", 146: "iso-tp0", 147: "iso-ip", 148: "jargon",
    149: "aed-512", 150: "sql-net", 151: "hems", 152: "bftp",
    153: "sgmp", 154: "netsc-prod", 155: "netsc-dev", 156: "sqlsrv",
    157: "knet-cmp", 158: "pcmail-srv", 159: "nss-routing",
    160: "sgmp-traps", 161: "snmp", 162: "snmp-trap", 163: "cmip-man",
    164: "cmip-agent", 165: "xns-courier", 166: "s-net", 167: "namp",
    168: "rsvd", 169: "send", 170: "print-srv", 171: "multiplex",
    172: "cl-1", 173: "xyplex-mux", 174: "mailq", 175: "vmnet",
    176: "genrad-mux", 177: "xdmcp", 178: "nextstep", 179: "bgp",
    180: "ris", 181: "unify", 182: "audit", 183: "ocbinder",
    184: "ocserver", 185: "remote-kis", 186: "kis", 187: "aci",
    188: "mumps", 189: "qft", 190: "gacp", 191: "prospero",
    192: "osu-nms", 193: "srmp", 194: "irc", 195: "dn6-nlm-aud",
    196: "dn6-smm-red", 197: "dls", 198: "dls-mon", 199: "smux",
    200: "src", 201: "at-rtmp", 202: "at-nbp", 203: "at-3",
    204: "at-echo", 205: "at-5", 206: "at-zis", 207: "at-7",
    208: "at-8", 209: "tam", 210: "z39.50", 211: "914c-g",
    212: "anet", 213: "ipx", 214: "vmpwscs", 215: "softpc",
    216: "cails", 217: "dbase", 218: "mpp", 219: "uarps",
    220: "imap3", 221: "fln-spx", 222: "rsh-spx", 223: "cdc",
    224: "masqdialer", 242: "direct", 243: "sur-meas", 244: "inbusiness",
    245: "link", 246: "dsp3270", 247: "subntbcst-tftp",
    248: "bhfhs", 249: "rap-ip", 250: "rap-sec",
    253: "vortex", 254: "vortex", 256: "rap", 257: "fw1-secureremote",
    258: "fw1-mc-fwmodule", 259: "esro-gen", 260: "openport",
    261: "nsiiops", 262: "arcisdms", 263: "hdap", 264: "bgmp",
    265: "x-bone-ctl", 266: "sst", 267: "td-service", 268: "td-replica",
    269: "manet", 270: "gist", 280: "http-mgmt", 281: "personal-link",
    282: "cableport-ax", 283: "rescap", 284: "corerjd",
    286: "fxp", 287: "k-block", 288: "novastorbakcup",
    294: "wap-push", 295: "wap-pushsecure", 296: "esip",
    297: "ottp", 298: "mpt", 299: "nsrexec",
    300: "remoteware", 301: "remoteware-cl", 302: "redwood-broker",
    303: "redwood-broker", 304: "sunlink-ftp", 305: "mcs-p", 306: "ls3bcast",
    307: "ls3", 308: "novastorbakcup", 309: "entrusttime", 310: "bhmds",
    311: "asip-webadmin", 312: "vslmp", 313: "magenta-logic",
    314: "opalis-robot", 315: "dpsi", 316: "decauth", 317: "zannet",
    318: "tsp", 319: "pcep", 320: "pcep-s", 321: "pip", 322: "rtsps",
    323: "rpki-rtr", 324: "rpki-rtr-tls", 326: "nsjtp-ctrl",
    327: "nsjtp-data", 328: "iscsi-target", 329: "iscsi-rx",
    330: "netconf-ssh", 331: "netconf-ssh", 332: "netconf-beep",
    333: "netconfsoaphttp", 344: "paws", 345: "paws-tls",
    346: "zserv", 347: "fatserv", 348: "csi-sgwp", 349: "mftp",
    350: "matip-type-a", 351: "matip-type-b", 352: "dtag-ste-sb",
    353: "ndsauth", 354: "bh611", 355: "datex-asn", 356: "cloanto-net-1",
    357: "bhevent", 358: "shrinkwrap", 359: "tenebris-nts",
    360: "scoi2odialog", 361: "semantix", 362: "srssend", 363: "rsvp-tunnel",
    364: "aurora-cmgr", 365: "dtk", 366: "odmr", 367: "mortgageware",
    368: "qbikgdp", 369: "rpc2portmap", 370: "codaauth2", 371: "clearcase",
    372: "ulistproc", 373: "legent-1", 374: "legent-2", 375: "hassle",
    376: "nip", 377: "tnETOS", 378: "dsETOS", 379: "is99c",
    380: "is99s", 381: "hp-collector", 382: "hp-managed-node",
    383: "hp-alarm-mgr", 384: "arns", 385: "ibm-app", 386: "asa",
    387: "aurp", 388: "unidata-ldm", 389: "ldap", 390: "uis",
    391: "synotics-relay", 392: "synotics-broker", 393: "dis",
    394: "embl-ndt", 395: "netcp", 396: "netware-ip", 397: "mptn",
    398: "kryptolan", 399: "iso-tsap-c2", 400: "work-sol",
    401: "ups", 402: "genie", 403: "decap", 404: "nced",
    405: "ncld", 406: "imsp", 407: "timbuktu", 408: "prm-sm",
    409: "prm-nm", 410: "decladebug", 411: "rmt", 412: "synoptics-trap",
    413: "smsp", 414: "infoseek", 415: "bnet", 416: "silverplatter",
    417: "onmux", 418: "hyper-g", 419: "ariel1", 420: "smpte",
    421: "ariel2", 422: "ariel3", 423: "opc-job-start", 424: "opc-job-track",
    425: "icad-el", 426: "smartsdp", 427: "svrloc", 428: "ocs-cmu",
    429: "ocs-amu", 430: "utmpsd", 431: "utmpcd", 432: "iasd",
    433: "nnsp", 434: "mobileip-agent", 435: "mobilip-mn", 436: "dna-cml",
    437: "comscm", 438: "dsfgw", 439: "dasp", 440: "sgcp",
    441: "decvms-sysmgt", 442: "cvc-hostd", 443: "https", 444: "snpp",
    445: "microsoft-ds", 446: "ddm-rdb", 447: "ddm-dfm", 448: "ddm-ssl",
    449: "as-servermap", 450: "tserver", 451: "sfs-smp-net",
    452: "sfs-config", 453: "creativeserver", 454: "contentserver",
    455: "creativepartnr", 456: "macon-tcp", 457: "scohelp",
    458: "appleqtc", 459: "ampr-rcmd", 460: "skronk", 461: "datasurfsrv",
    462: "datasurfsrvsec", 463: "alpes", 464: "kpasswd5", 465: "urd",
    466: "digital-vrc", 467: "mylex-mapd", 468: "photuris", 469: "rcp",
    470: "scx-proxy", 471: "mondex", 472: "ljk-login", 473: "hybrid-pop",
    474: "tn-tl-w1", 475: "tcpnethaspsrv", 476: "tn-tl-fd1",
    477: "ss7ns", 478: "spsc", 479: "iafserver", 480: "iafdbase",
    481: "ph", 482: "bgs-nsi", 483: "ulpnet", 484: "integra-sme",
    485: "powerburst", 486: "avian", 487: "saft", 488: "gss-http",
    489: "nest-protocol", 490: "micom-pfs", 491: "go-login", 492: "ticf-1",
    493: "ticf-2", 494: "pov-ray", 495: "intecourier", 496: "pim-rp-disc",
    497: "retrospect", 498: "siam", 499: "iso-ill", 500: "isakmp",
    501: "stmf", 502: "modbus", 503: "intrinsa", 504: "citadel",
    505: "mailbox-lm", 506: "ohimsrv", 507: "crs", 508: "xvttp",
    509: "snare", 510: "fcp", 511: "passgo", 512: "exec", 513: "login",
    514: "shell", 515: "printer", 516: "videotex", 517: "talk",
    518: "ntalk", 519: "utime", 520: "efs", 521: "ripng",
    522: "ulp", 523: "ibm-db2", 524: "ncp", 525: "timed",
    526: "tempo", 527: "stx", 528: "custix", 529: "irc-serv",
    530: "courier", 531: "conference", 532: "netnews", 533: "netwall",
    534: "windream", 535: "iiop", 536: "opalis-rdv", 537: "nmsp",
    538: "gdomap", 539: "apertus-ldp", 540: "uucp", 541: "uucp-rlogin",
    542: "commerce", 543: "klogin", 544: "kshell", 545: "appleqtcsrvr",
    546: "dhcpv6-client", 547: "dhcpv6-server", 548: "afpovertcp",
    549: "idfp", 550: "new-rwho", 551: "cybercash", 552: "devshr-nts",
    553: "pirp", 554: "rtsp", 555: "dsf", 556: "remotefs",
    557: "openvms-sysipc", 558: "sdnskmp", 559: "teedtap", 560: "rmonitor",
    561: "monitor", 562: "chshell", 563: "nntps", 564: "9pfs",
    565: "whoami", 566: "streettalk", 567: "banyan-rpc", 568: "ms-shuttle",
    569: "ms-rome", 570: "meter", 571: "meter", 572: "sonar",
    573: "banyan-vip", 574: "ftp-agent", 575: "vemmi", 576: "ipcd",
    577: "vnas", 578: "ipdd", 579: "decbsrv", 580: "sntp-heartbeat",
    581: "bdp", 582: "scc-security", 583: "philips-vc", 584: "keyserver",
    585: "imap4-ssl", 586: "password-chg", 587: "submission", 588: "cal",
    589: "eyelink", 590: "tns-cml", 591: "http-rpc-epmap",
    592: "filemaker-jdbc", 593: "http-alt", 594: "tcp-id-port",
    595: "vpnz", 596: "smsd", 597: "ptcnameservice", 598: "sco-websrvrmg3",
    599: "acp", 600: "ipcserver", 601: "syslog-conn", 602: "xmlrpc-beep",
    603: "idxp", 604: "tunnel", 605: "soap-beep", 606: "urm",
    607: "nqs", 608: "sift-uft", 609: "npmp-trap", 610: "npmp-local",
    611: "npmp-gui", 612: "hmmp-ind", 613: "hmmp-op", 614: "sshell",
    615: "sco-inetmgr", 616: "sco-sysmgr", 617: "sco-dtmgr",
    618: "dei-icda", 619: "compaq-evm", 620: "sco-websrvrmgr",
    621: "escp-ip", 622: "collaborator", 623: "asf-rmcp", 624: "cryptoadmin",
    625: "dec-dlm", 626: "asia", 627: "passgo-tivoli", 628: "qmqp",
    629: "3com-amp3", 630: "rda", 631: "ipp", 632: "bmpp",
    633: "servstat", 634: "ginad", 635: "rlzdbase", 636: "ldaps",
    637: "lanserver", 638: "mcns-sec", 639: "msdp", 640: "entrust-sps",
    641: "repcmd", 642: "esro-emsdp", 643: "sanity", 644: "dwr",
    645: "pssc", 646: "ldp", 647: "dhcp-failover",
    648: "rrp", 649: "cadview-3d", 650: "obex", 651: "ieee-mms",
    652: "hello-port", 653: "repscmd", 654: "aodv", 655: "tinc",
    656: "spmp", 657: "rmc", 658: "tenfold", 659: "url-rendezvous",
    660: "mac-srvr-admin", 661: "hap", 662: "pftp", 663: "purenoise",
    664: "asf-secure-rmcp", 665: "sun-dr", 666: "doom", 667: "camp",
    668: "mecomm", 669: "meregister", 670: "vacdsm-app", 671: "vacdsm-sws",
    672: "vacdsm-vpp", 673: "vacdsm-vport", 674: "acap", 675: "decpas",
    676: "vpps-qua", 677: "vpps-via", 678: "vpp", 679: "ggf-ncp",
    680: "mrm", 681: "entrust-aaas", 682: "entrust-aams",
    683: "xfr", 684: "corba-iiop", 685: "corba-iiop-ssl",
    686: "mdc-portmapper", 687: "hcp-wismar", 688: "asipregistry",
    689: "realm-rusd", 690: "vatp", 691: "msexch-routing",
    692: "hyperwave-isp", 693: "connendp", 694: "ha-cluster",
    695: "ieee-mms-ssl", 696: "rushd", 697: "uuidgen", 698: "olsr",
    699: "accessnetwork", 700: "epp", 701: "lmp", 702: "iris-beep",
    703: "iris-xpc", 704: "iris-xpcs", 705: "agentx",
    706: "silc", 707: "borland-dsj", 708: "entrust-kmsh",
    709: "entrust-ash", 710: "cisco-tdp", 711: "cisco-tdp", 712: "tbrpf",
    713: "iris-xpc", 714: "iris-xpcs", 715: "iris-lwz", 716: "pana",
    717: "sd-broker", 720: "smarts-notify", 721: "smarts-status",
    722: "smarts-service", 729: "netviewdm1", 730: "netviewdm2",
    731: "netviewdm3", 741: "netgw", 742: "netrcs", 744: "flexlm",
    747: "fujitsu-dev", 748: "ris-cm", 749: "kerberos-adm",
    750: "kerberos-iv", 751: "pump", 752: "qrh", 753: "rrh",
    754: "tell", 758: "nlogin", 759: "con", 760: "ns", 761: "rxe",
    762: "quotad", 763: "cycleserv", 764: "omserv", 765: "webster",
    767: "phonebook", 769: "vid", 770: "cadlock", 771: "rtip",
    772: "cycleserv2", 773: "submit", 774: "rpasswd", 775: "entomb",
    776: "wpages", 777: "multiling-http", 780: "wpgs", 781: "hp-managed-node",
    782: "hp-alarm-mgr", 800: "mdbs-daemon", 801: "device", 802: "mbap-s",
    804: "oftps", 805: "protel-sccp", 806: "netglish", 808: "ccproxy-http",
    810: "fcp-udp", 818: "remotefs", 819: "ideafarm-door", 820: "ideafarm-panic",
    828: "itm-mcell-s", 829: "pkix-3-ca-ra", 830: "netconf-ssh",
    831: "netconf-beep", 832: "netconfsoaphttp", 833: "netconfsoapbeep",
    847: "dhcp-failover2", 848: "gdoi", 853: "domain-s", 854: "dlep-radio",
    855: "dlep-proto", 860: "iscsi", 861: "owamp-control", 862: "twamp-control",
    873: "rsync", 886: "iclcnet-locate", 887: "iclcnet-svinfo",
    888: "accessbuilder", 900: "omginitialrefs", 901: "smpnameres",
    902: "ideafarm-chat", 903: "ideafarm-catch", 910: "kink",
    911: "xact-backup", 912: "apex-mesh", 913: "apex-edge",
    950: "oftep", 953: "rndc", 954: "ptcnameservice",
    985: "infinidb", 989: "ftps-data", 990: "ftps", 991: "nas",
    992: "telnets", 993: "imaps", 994: "ircs", 995: "pop3s",
    996: "xtreelic", 997: "maitrd", 998: "busboy", 999: "garcon",
    1000: "cadlock", 1001: "webpush", 1002: "windows-icfw",
    1003: "ifor-protocol", 1004: "ifor-protocol", 1005: "ifor-protocol",
    1006: "ifor-protocol", 1007: "ifor-protocol", 1008: "ufsd",
    1009: "neod1", 1010: "neod2", 1011: "dns-ch",
    1023: "smartcard-tls",

    # Registered ports (1024-49151)
    1025: "msrpc", 1080: "socks", 1194: "openvpn",
    1241: "nessus", 1311: "dell-openmanage", 1337: "waste",
    1433: "mssql", 1434: "mssql-browser", 1471: "hak5",
    1512: "wins", 1521: "oracle", 1589: "cisco-vqp",
    1701: "l2tp", 1723: "pptp", 1748: "oracle-em1",
    1755: "mms", 1812: "radius", 1813: "radius-acct",
    1863: "msn", 1900: "upnp", 1985: "cisco-hsrp",
    2000: "cisco-sccp", 2002: "globe", 2049: "nfs",
    2082: "cpanel", 2083: "cpanel-ssl", 2096: "whm",
    2100: "amiganetfs", 2181: "zookeeper", 2222: "directadmin",
    2302: "halo", 2375: "docker", 2376: "docker-ssl",
    2404: "iec-104", 2483: "oracle-db", 2484: "oracle-db-ssl",
    2535: "madcap", 2546: "evault", 2593: "ultima-online",
    2710: "sso-service", 2967: "symantec-av", 3000: "grafana",
    3001: "nessus-web", 3050: "gds-db", 3074: "xbox-live",
    3128: "squid", 3260: "iscsi", 3306: "mysql",
    3310: "clamav", 3389: "rdp", 3396: "novell-ndps",
    3455: "rsvp-port", 3478: "stun", 3479: "stun-tls",
    3493: "nut", 3544: "teredo", 3632: "distcc",
    3659: "apple-sasl", 3689: "daap", 3690: "svn",
    3724: "blizzard", 3784: "bfd-control", 3785: "bfd-echo",
    3872: "oem-agent", 3900: "uddi", 3945: "emcp",
    4000: "diablo2", 4007: "print-srv", 4089: "opencore",
    4093: "pxe", 4111: "xgrid", 4156: "statd",
    4190: "sieve", 4226: "ale", 4242: "vrml-multi-use",
    4321: "rwhois", 4333: "msql", 4444: "krb524",
    4486: "icms", 4500: "ipsec-nat-t", 4567: "sinatra",
    4662: "edonkey", 4713: "pulse-audio", 4728: "capm",
    4840: "opc-ua", 4843: "opc-ua-tls", 4899: "radmin",
    5000: "upnp", 5001: "upnp-tls", 5050: "mmcc",
    5060: "sip", 5061: "sip-tls", 5100: "admd",
    5150: "escp", 5190: "icq", 5222: "xmpp",
    5223: "xmpp-ssl", 5228: "android-c2dm", 5269: "xmpp-server",
    5308: "cfengine", 5353: "mdns", 5355: "llmnr",
    5357: "wsdapi", 5400: "excerpt", 5432: "postgresql",
    5433: "postgresql-test", 5500: "vnc", 5555: "adb",
    5556: "adb", 5601: "kibana", 5631: "pcanywhere",
    5632: "pcanywhere-stat", 5672: "amqp", 5671: "amqps",
    5693: "nessus", 5722: "dfsr", 5800: "vnc-web",
    5900: "vnc", 5901: "vnc-1", 5938: "teamviewer",
    5984: "couchdb", 5985: "winrm-http", 5986: "winrm-https",
    5999: "cvsup", 6000: "x11", 6001: "x11-1",
    6129: "dameware", 6257: "winmx", 6346: "gnutella",
    6347: "gnutella2", 6379: "redis", 6380: "redis-ssl",
    6443: "k8s-api", 6464: "ieee-11073", 6514: "syslog-tls",
    6665: "irc", 6666: "irc", 6667: "irc", 6668: "irc",
    6669: "irc", 6679: "osaut", 6881: "bittorrent",
    6891: "bittorrent", 6900: "bittorrent", 6969: "acmsoda",
    6970: "quic", 7000: "avira", 7001: "avira",
    7002: "avira", 7199: "cassandra", 7435: "winlogon",
    7474: "neo4j", 7547: "cwmp", 7648: "cusoft",
    7707: "emby", 7777: "cbt", 7880: "powercode",
    8000: "http-alt", 8008: "http-alt", 8009: "ajp",
    8010: "xmpp-file", 8080: "http-alt", 8081: "http-alt",
    8086: "influxdb", 8096: "emby-web", 8100: "console",
    8123: "polipo", 8125: "statsd", 8140: "puppet",
    8200: "elasticsearch", 8222: "vmware-http", 8291: "winbox",
    8300: "consul", 8333: "bitcoin", 8383: "m2mservices",
    8400: "cvd", 8443: "https-alt", 8448: "matrix",
    8484: "websync", 8529: "arangodb", 8530: "ws-discovery",
    8531: "ws-discovery-tls", 8580: "freelance", 8600: "asterisk",
    8611: "canon-bjnp", 8612: "canon-bjnp1", 8621: "ace-server",
    8622: "ace-secure", 8697: "ultraseek", 8765: "ultraseek2",
    8880: "cddbp-alt", 8883: "mqtts", 8888: "http-alt",
    9000: "sonarqube", 9001: "tor-orport", 9002: "dynamo",
    9030: "tor-dirport", 9042: "cassandra", 9050: "tor-socks",
    9060: "websm", 9080: "glrpc", 9090: "prometheus",
    9091: "transmission", 9092: "h2database", 9100: "jetdirect",
    9119: "mxit", 9150: "tor-socks", 9191: "cat-publish",
    9200: "elasticsearch", 9300: "ibm-cics", 9332: "litecoin",
    9333: "litecoin-test", 9389: "adws", 9418: "git",
    9443: "vmware-https", 9527: "qconn", 9535: "mngsuite",
    9595: "pds", 9600: "omron-fins", 9669: "xmms2",
    9696: "content-filter", 9800: "webdav", 9875: "sap-v1",
    9898: "monkeycom", 9987: "ts3", 9993: "starface-voip",
    9997: "splunk-mgmt", 9999: "abyss",

    # Commonly used high ports
    10000: "webmin", 10001: "scp-config", 10010: "rxapi",
    10050: "zabbix-agent", 10051: "zabbix-server",
    10161: "snmp-agents", 11000: "irisa", 11211: "memcached",
    11300: "rabbitmq", 11371: "pgp-keyserver", 12000: "cce4x",
    12345: "netbus", 12489: "ns-client", 12975: "logmein",
    13720: "symantec-endpoint", 13721: "symantec-endpoint",
    13724: "vnetd", 13782: "bpcd", 13783: "bpjava-msvc",
    14567: "bf1942", 15000: "hypterm", 15118: "dipnet",
    15555: "direct-play", 16010: "bmcperf-agent", 16379: "redis-cluster",
    16452: "cisco-ipsla", 17000: "bitfighter", 17300: "kuang2",
    17500: "db-lsp", 18104: "radpdf", 18264: "checkpoint",
    18888: "liquidsoap", 19226: "panda-av", 19283: "keysrvr",
    19315: "keyshadow", 19350: "munnin", 19541: "jcp-client",
    19780: "ultraseek-db", 20000: "dnp", 20560: "knetd",
    21000: "irtrans", 21025: "pareto", 22136: "flir",
    22222: "davis", 22347: "wibu", 22350: "codemeter",
    23456: "evilftp", 24554: "binkp", 24800: "synergy",
    25000: "icl-twobase", 25001: "icl-twobase1", 25003: "icl-twobase2",
    25005: "icl-twobase3", 25007: "icl-twobase4", 25565: "minecraft",
    25901: "ncompress", 27000: "flexlm", 27017: "mongodb",
    27018: "mongodb-web", 27374: "sub7", 28000: "pq-lic-mgr",
    28015: "rethinkdb", 28017: "mongodb-config", 28784: "ae-server",
    30000: "ndmps", 30718: "lanss", 31119: "delta",
    31337: "back-orifice", 31416: "boinc", 31457: "tetrinet",
    32768: "filenet-tms", 32769: "filenet-rpc", 32770: "filenet-nch",
    33434: "traceroute", 37777: "dahua-dvr", 40000: "safety",
    44818: "ethernet-ip", 47808: "bacnet", 49152: "windows-rpc",
    49153: "windows-rpc", 49154: "windows-rpc", 49155: "windows-rpc",
    49156: "windows-rpc", 49157: "windows-rpc", 50000: "ibm-db2",
    50030: "hadoop-nn", 50070: "hadoop-dn", 50075: "hadoop-webhdfs",
    50090: "hadoop-snn", 54200: "veeam", 54328: "splunk-mgmt-ssl",
    55600: "oracle-oem", 60000: "deepview", 60020: "deepview-ssl",
    61439: "netprowler", 61440: "netprowler-mgr", 62078: "iphone-sync",
    64738: "ms-sip", 65301: "pcanywhere-def",
}


def get_service_name(port: int) -> str:
    return SERVICE_NAMES.get(port, "unknown")


def parse_ip_target(target: str) -> list[str]:
    target = target.strip()
    if not target:
        raise ValueError("Empty target")

    # CIDR notation: 192.168.1.0/24
    if "/" in target:
        try:
            network = IPv4Network(target, strict=False)
            return [str(host) for host in network.hosts()]
        except (AddressValueError, ValueError) as e:
            raise ValueError(f"Invalid CIDR target '{target}': {e}") from e

    # Range notation: 192.168.1.1-192.168.1.10
    if "-" in target:
        parts = target.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid IP range '{target}': expected 'start-end'")
        try:
            start = IPv4Address(parts[0].strip())
            end = IPv4Address(parts[1].strip())
        except AddressValueError as e:
            raise ValueError(f"Invalid IP in range '{target}': {e}") from e
        if start > end:
            raise ValueError(f"Invalid range '{target}': start > end")
        return [str(IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]

    # Single IP or hostname
    return [target]


def parse_port_range(port_str: str) -> list[int]:
    port_str = port_str.strip()
    if not port_str:
        raise ValueError("Empty port specification")

    ports: list[int] = []
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            range_parts = part.split("-")
            if len(range_parts) != 2:
                raise ValueError(f"Invalid port range '{part}': expected 'start-end'")
            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
            except ValueError as e:
                raise ValueError(f"Invalid port number in '{part}': {e}") from e
            if start > end:
                raise ValueError(f"Invalid port range '{part}': start > end")
            if start < 1 or end > 65535:
                raise ValueError(f"Ports must be 1-65535, got '{part}'")
            ports.extend(range(start, end + 1))
        else:
            try:
                port = int(part)
            except ValueError as e:
                raise ValueError(f"Invalid port '{part}': {e}") from e
            if port < 1 or port > 65535:
                raise ValueError(f"Port must be 1-65535, got {port}")
            ports.append(port)

    if not ports:
        raise ValueError("No ports specified")
    return ports


def export_json(results: list[HostResult], filepath: str) -> None:
    data = []
    for host in results:
        data.append({
            "host": host.host,
            "status": host.status.value,
            "scan_time": host.scan_time,
            "error_message": host.error_message,
            "open_ports": [
                {
                    "port": r.port,
                    "service": r.service,
                    "error_message": r.error_message,
                }
                for r in host.open_ports
            ],
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_csv(results: list[HostResult], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "status", "service", "error_message"])
        for host in results:
            if host.open_ports:
                for r in host.open_ports:
                    writer.writerow([r.host, r.port, r.status.value, r.service, r.error_message])
            else:
                writer.writerow([host.host, "", host.status.value, "", host.error_message])
