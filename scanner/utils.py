import csv
import json
import socket
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from scanner.engine import HostResult

SERVICE_NAMES: dict[int, str] = {
    # Well-known system ports (0-1023)
    1: "tcpmux", 7: "echo", 9: "discard", 13: "daytime", 17: "qotd",
    19: "chargen", 20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet",
    25: "smtp", 37: "time", 42: "nameserver", 43: "whois",
    53: "dns", 67: "dhcp-server", 68: "dhcp-client", 69: "tftp",
    70: "gopher", 79: "finger", 80: "http", 88: "kerberos",
    109: "pop2", 110: "pop3", 111: "rpcbind", 113: "ident",
    119: "nntp", 123: "ntp", 135: "msrpc", 137: "netbios-ns",
    138: "netbios-dgm", 139: "netbios-ssn", 143: "imap",
    161: "snmp", 162: "snmp-trap", 177: "xdmcp", 179: "bgp",
    194: "irc", 201: "apple-talk", 264: "bgmp", 318: "tsp",
    381: "hp-openview", 383: "hp-alarm-mgr", 389: "ldap",
    411: "directconnect", 443: "https", 445: "smb",
    464: "kerberos-admin", 465: "smtps", 497: "retrospect",
    500: "isakmp", 512: "exec", 513: "login", 514: "shell",
    515: "printer", 520: "rip", 521: "ripng", 540: "uucp",
    543: "klogin", 544: "kshell", 546: "dhcpv6-client",
    547: "dhcpv6-server", 548: "afp", 554: "rtsp", 556: "remotefs",
    563: "nntps", 587: "smtp-submit", 591: "filemaker",
    593: "rpc-over-http", 631: "ipp", 636: "ldaps",
    639: "msdp", 646: "ldp", 691: "msexch-routing",
    749: "kerberos-adm", 750: "kerberos-iv", 853: "dns-over-tls",
    873: "rsync", 902: "vmware-server", 989: "ftps-data",
    990: "ftps", 993: "imaps", 995: "pop3s",

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
