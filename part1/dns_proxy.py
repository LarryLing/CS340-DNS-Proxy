from asyncio import TimeoutError, get_event_loop, wait_for
from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack

from constants import DNS_TYPES, LOCAL_IP, LOCAL_PORT, RESOLVER_IP, RESOLVER_PORT


class DNSProxy:
    def __init__(self):
        self.proxy_address = (LOCAL_IP, LOCAL_PORT)
        self.resolver_address = (RESOLVER_IP, RESOLVER_PORT)
        self.transport = None

    async def handle_client(self, query_packet, client_address):
        self.log_packet(query_packet, self.proxy_address)

        response_packet = await self.invoke_upstream_resolver(query_packet)

        if response_packet:
            self.log_packet(response_packet, self.resolver_address)
            self.transport.sendto(response_packet, client_address)
        else:
            print(f"Failed to communicate with upstream resolver for {client_address}")

    async def invoke_upstream_resolver(self, query_packet, max_attempts=3):
        resolver_socket = socket(AF_INET, SOCK_DGRAM)
        resolver_socket.setblocking(False)

        loop = get_event_loop()

        try:
            for attempt in range(1, max_attempts + 1):
                try:
                    await loop.sock_sendto(
                        resolver_socket, query_packet, self.resolver_address
                    )

                    response_packet, _ = await wait_for(
                        loop.sock_recvfrom(resolver_socket, 2048), timeout=5.0
                    )

                    return response_packet

                except TimeoutError:
                    print(
                        f"Timeout waiting for response from {self.resolver_address} (Attempt {attempt}/{max_attempts})"
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
