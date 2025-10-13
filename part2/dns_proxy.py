from asyncio import get_event_loop
from struct import unpack

from constants import (
    DNS_TYPE_FUNCTIONS,
    DNS_TYPES,
    LOCAL_IP,
    LOCAL_PORT,
    RESOLVER_IP,
    RESOLVER_PORT,
)
from dnslib import RR, DNSHeader, DNSQuestion, DNSRecord
from requests import get


class DNSProxy:
    def __init__(self):
        self.proxy_address = (LOCAL_IP, LOCAL_PORT)
        self.resolver_address = (RESOLVER_IP, RESOLVER_PORT)
        self.transport = None

    async def handle_client(self, query_packet, client_address):
        self.log_packet(query_packet, self.proxy_address)

        response_packet = await self.invoke_doh_resolver(query_packet)

        if response_packet:
            self.log_packet(response_packet, self.resolver_address)
            self.transport.sendto(response_packet, client_address)
        else:
            print(f"Failed to communicate with DoH API resolver for {client_address}")

    async def invoke_doh_resolver(self, query_packet, max_attempts=3):
        dns_query = DNSRecord.parse(query_packet)

        domain_name = dns_query.questions[0].qname
        record_type = dns_query.questions[0].qtype

        url = f"https://dns.google/resolve?name={domain_name}&type={DNS_TYPES[record_type]}"

        loop = get_event_loop()

        for attempt in range(1, max_attempts + 1):
            try:
                http_response = await loop.run_in_executor(None, get, url)
                http_response.raise_for_status()
                response_json_data = http_response.json()

                response_packet = self.build_dns_response(dns_query, response_json_data)

                return response_packet

            except Exception as e:
                print(
                    f"An error occurred while communicating with DoH API resolver: {e} (Attempt {attempt}/{max_attempts})"
                )

        return None

    def build_dns_response(self, query_data, doh_response):
        question = query_data.questions[0]

        dns_response = DNSRecord(
            DNSHeader(
                id=query_data.header.id,
                qr=1,
                aa=0,
                ra=1,
                rcode=doh_response.get("Status", 0),
            ),
            q=DNSQuestion(question.qname, question.qtype),
        )

        for answer in doh_response.get("Answer", []):
            dns_response.add_answer(
                RR(
                    answer["name"],
                    answer["type"],
                    ttl=answer["TTL"],
                    rdata=DNS_TYPE_FUNCTIONS[answer["type"]](answer["data"]),
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
