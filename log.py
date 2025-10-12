import struct


def log_data(address, data, offset=12):
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

    labels = []
    current_offset = offset

    while True:
        length = data[current_offset]
        current_offset += 1

        if length == 0:
            break

        label = data[current_offset : current_offset + length].decode("ascii")
        labels.append(label)

        current_offset += length

    dns_type = struct.unpack("!H", data[current_offset : current_offset + 2])[0]

    print(
        f"{address[0]}: {'.'.join(labels)}, Type {DNS_TYPES[dns_type]}, {len(data)} bytes"
    )
