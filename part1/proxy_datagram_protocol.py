from asyncio import DatagramProtocol, create_task


class ProxyDatagramProtocol(DatagramProtocol):
    def __init__(self, dns_proxy):
        self.dns_proxy = dns_proxy

    def connection_made(self, transport):
        self.dns_proxy.transport = transport

    def datagram_received(self, query_packet, query_address):
        create_task(self.dns_proxy.handle_client(query_packet, query_address))
