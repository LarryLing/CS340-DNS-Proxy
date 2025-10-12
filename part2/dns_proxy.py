import asyncio
import socket
import struct

from constants import DNS_TYPES, LOCAL_IP, LOCAL_PORT, RESOLVER_IP, RESOLVER_PORT


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
            print(f"Failed to communicate with upstream resolver for {client_address}")

    async def query_resolver(self, data, max_tries=3):
        resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        resolver_socket.setblocking(False)

        loop = asyncio.get_event_loop()

        try:
            for tries in range(max_tries):
                try:
                    await loop.sock_sendto(resolver_socket, data, self.resolver_address)

                    resolver_message, _ = await asyncio.wait_for(
                        loop.sock_recvfrom(resolver_socket, 2048), timeout=5.0
                    )

                    return resolver_message

                except asyncio.TimeoutError:
                    print(
                        f"Timeout waiting for response from {self.resolver_address} (Attempt {tries + 1}/{max_tries})"
                    )

                except Exception as e:
                    print(
                        f"An error occurred while communicating with upstream resolver: {e} (Attempt {tries + 1}/{max_tries})"
                    )

        finally:
            resolver_socket.close()

        return None

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

        dns_type = struct.unpack("!H", data[current_offset : current_offset + 2])[0]

        print(
            f"{address[0]}: {'.'.join(labels)}, Type {DNS_TYPES[dns_type]}, {len(data)} bytes"
        )
