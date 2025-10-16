from asyncio import TimeoutError, get_running_loop, wait_for
from json import dump
from os import path
from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack
from time import time

from constants import DNS_TYPES, LOCAL_ADDR, LOG_FILENAME, RESOLVER_ADDR


class DNSProxy:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(LOCAL_ADDR)
        self.socket.setblocking(False)
        self.logs = []

    async def handle_query(self, query_packet, client_address):
        self.log_packet(query_packet, LOCAL_ADDR)

        response_packet = await self.invoke_upstream_resolver(query_packet)

        if response_packet:
            self.log_packet(response_packet, RESOLVER_ADDR)

            loop = get_running_loop()
            await loop.sock_sendto(self.socket, response_packet, client_address)
        else:
            print(f"Failed to communicate with upstream resolver for {client_address}")

    async def invoke_upstream_resolver(self, query_packet, max_attempts=3):
        resolver_socket = socket(AF_INET, SOCK_DGRAM)
        resolver_socket.setblocking(False)

        loop = get_running_loop()

        try:
            for attempt in range(1, max_attempts + 1):
                try:
                    await loop.sock_sendto(resolver_socket, query_packet, RESOLVER_ADDR)

                    response_packet, _ = await wait_for(
                        loop.sock_recvfrom(resolver_socket, 2048), timeout=5.0
                    )

                    return response_packet

                except TimeoutError:
                    print(
                        f"Timeout waiting for response from {RESOLVER_ADDR} (Attempt {attempt}/{max_attempts})"
                    )

                except Exception as e:
                    print(
                        f"An error occurred while communicating with upstream resolver: {e} (Attempt {attempt}/{max_attempts})"
                    )

        finally:
            resolver_socket.close()

        return None

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
            f"{path.dirname(path.realpath(__file__))}/{LOG_FILENAME}", "a"
        ) as log_file:
            dump(self.logs, log_file, indent=2)
