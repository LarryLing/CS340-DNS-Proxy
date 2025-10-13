from asyncio import Event, get_event_loop, run

from constants import LOCAL_IP, LOCAL_PORT
from dns_proxy import DNSProxy
from proxy_datagram_protocol import ProxyDatagramProtocol


async def main():
    dns_proxy = DNSProxy()

    loop = get_event_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ProxyDatagramProtocol(dns_proxy), local_addr=(LOCAL_IP, LOCAL_PORT)
    )

    try:
        await Event().wait()

    except KeyboardInterrupt:
        print("\nExiting...")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    finally:
        transport.close()
        print("\nDNS proxy closed successfully")


if __name__ == "__main__":
    try:
        run(main())

    except KeyboardInterrupt:
        pass
