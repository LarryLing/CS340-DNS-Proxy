import dnslib

LOCAL_IP = "127.0.0.1"
LOCAL_PORT = 1053

RESOLVER_IP = "8.8.8.8"
RESOLVER_PORT = 53

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
    1: dnslib.A,
    2: dnslib.NS,
    5: dnslib.CNAME,
    6: dnslib.SOA,
    12: dnslib.PTR,
    15: dnslib.MX,
    16: dnslib.TXT,
    28: dnslib.AAAA,
    33: dnslib.SRV,
}
