from dnslib import AAAA, CNAME, MX, NS, PTR, SOA, SRV, TXT, A

LOCAL_IP = "127.0.0.1"
LOCAL_PORT = 1053
LOCAL_ADDR = (LOCAL_IP, LOCAL_PORT)

RESOLVER_IP = "8.8.8.8"
RESOLVER_PORT = 53
RESOLVER_ADDR = (RESOLVER_IP, RESOLVER_PORT)

LOG_FILENAME = "dns_log.json"

DNS_TYPES = {
    1: "A",
    2: "NS",
    5: "CNAME",
    6: "SOA",
    12: "PTR",
    15: "MX",
    16: "TXT",
    28: "AAAA",
    33: "SRV",
    41: "OPT",
    255: "ANY",
}

DNS_TYPE_FUNCTIONS = {
    1: A,
    2: NS,
    5: CNAME,
    6: SOA,
    12: PTR,
    15: MX,
    16: TXT,
    28: AAAA,
    33: SRV,
}
