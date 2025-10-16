from asyncio import get_running_loop
from functools import partial
from json import dump
from os import path
from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack
from time import time

from constants import (
    DNS_TYPE_FUNCTIONS,
    DNS_TYPES,
    LOCAL_ADDR,
    LOG_FILENAME,
    RESOLVER_ADDR,
)
from dnslib import RR, DNSRecord
from requests import get


class DNSProxy:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(LOCAL_ADDR)
        self.socket.setblocking(False)
        self.logs = []

    async def handle_query(self, query_packet, client_address):
        self.log_packet(query_packet, LOCAL_ADDR)

        response_packet = await self.invoke_doh_resolver(query_packet)

        if response_packet:
            self.log_packet(response_packet, RESOLVER_ADDR)

            loop = get_running_loop()
            await loop.sock_sendto(self.socket, response_packet, client_address)
        else:
            print(f"Failed to communicate with DoH API resolver for {client_address}")

    async def invoke_doh_resolver(self, query_packet, max_attempts=3):
        dns_query = DNSRecord.parse(query_packet)

        domain_name = dns_query.questions[0].qname
        record_type = dns_query.questions[0].qtype

        url = f"https://dns.google/resolve?name={domain_name}&type={DNS_TYPES[record_type]}"

        loop = get_running_loop()

        for attempt in range(1, max_attempts + 1):
            try:
                http_response = await loop.run_in_executor(
                    None, partial(get, url, timeout=5)
                )
                http_response.raise_for_status()
                response_json_data = http_response.json()

                response_packet = self.build_dns_response(dns_query, response_json_data)

                return response_packet

            except Exception as e:
                print(
                    f"An error occurred while communicating with DoH API resolver: {e} (Attempt {attempt}/{max_attempts})"
                )

        return None

    def build_dns_response(self, dns_query, doh_response):
        dns_response = dns_query.reply()

        for answer in doh_response.get("Answer", []):
            dns_response.add_answer(
                RR(
                    answer["name"],
                    answer["type"],
                    ttl=answer["TTL"],
                    rdata=DNS_TYPE_FUNCTIONS[answer["type"]](answer["data"]),
                )
            )

        for authority in doh_response.get("Authority", []):
            dns_response.add_auth(
                RR(
                    authority["name"],
                    authority["type"],
                    ttl=authority["TTL"],
                    rdata=DNS_TYPE_FUNCTIONS[authority["type"]](authority["data"]),
                )
            )

        return dns_response.pack()

    def log_packet(self, packet, address):
        labels = []
        current_offset = 12

        while True:
            label_length = packet[current_offset]
            current_offset += 1

            if label_length == 0:
                break

            label = packet[current_offset : current_offset + label_length].decode(
                "ascii"
            )
            labels.append(label)

            current_offset += label_length

        record_type = unpack("!H", packet[current_offset : current_offset + 2])[0]

        print(
            f"{address}: {'.'.join(labels)}, Type {DNS_TYPES[record_type]}, {len(packet)} bytes"
        )

        self.logs.append(
            {
                "address": address,
                "name": ".".join(labels),
                "type": DNS_TYPES[record_type],
                "length": len(packet),
                "sent_at": int(time()),
            }
        )

    def cleaup(self):
        self.socket.close()

        with open(
            f"{path.dirname(path.realpath(__file__))}/{LOG_FILENAME}", "w"
        ) as log_file:
            dump(self.logs, log_file, indent=2)
