from asyncio import TimeoutError
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

    async def handle_client(self, data, client_address):
        self.log(data, self.proxy_address)

        resolver_message = await self.query_resolver(data)

        if resolver_message:
            self.log(resolver_message, self.resolver_address)
            self.transport.sendto(resolver_message, client_address)
        else:
            print(f"Failed to communicate with DoH API resolver for {client_address}")

    async def query_resolver(self, data, max_tries=3):
        parsed_query_data = DNSRecord.parse(data)

        query_name = parsed_query_data.questions[0].qname
        query_type = parsed_query_data.questions[0].qtype

        url = (
            f"https://dns.google/resolve?name={query_name}&type={DNS_TYPES[query_type]}"
        )

        for tries in range(max_tries):
            try:
                response = get(url)

                resolver_message = self.build_response_packet(
                    parsed_query_data, response.json()
                )

                return resolver_message

            except Exception as e:
                print(
                    f"An error occurred while communicating with DoH API resolver: {e} (Attempt {tries + 1}/{max_tries})"
                )

            except TimeoutError:
                print(
                    f"Timeout waiting for response from DoH API resolver (Attempt {tries + 1}/{max_tries})"
                )

        return None

    def build_response_packet(self, query_data, response_data):
        transaction_id = query_data.header.id
        query_name = query_data.questions[0].qname
        query_type = query_data.questions[0].qtype

        dns_response_packet = DNSRecord(
            DNSHeader(id=transaction_id, qr=1, aa=0, ra=1),
            q=DNSQuestion(query_name, query_type),
        )

        for answer in response_data["Answer"]:
            answer_name, answer_type, answer_ttl, answer_data = answer.values()

            dns_response_packet.add_answer(
                RR(
                    answer_name,
                    answer_type,
                    ttl=answer_ttl,
                    rdata=DNS_TYPE_FUNCTIONS[answer_type](answer_data),
                )
            )

        return dns_response_packet.pack()

    def log(self, data, address, offset=12):
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

        dns_type = unpack("!H", data[current_offset : current_offset + 2])[0]

        print(
            f"{address}: {'.'.join(labels)}, Type {DNS_TYPES[dns_type]}, {len(data)} bytes"
        )
