from asyncio import create_task, get_running_loop, run

from dns_proxy import DNSProxy


async def main():
    dns_proxy = DNSProxy()

    loop = get_running_loop()

    try:
        while True:
            query_packet, client_address = await loop.sock_recvfrom(
                dns_proxy.socket, 2048
            )

            create_task(dns_proxy.handle_query(query_packet, client_address))

    finally:
        dns_proxy.cleaup()


if __name__ == "__main__":
    try:
        run(main())

    except KeyboardInterrupt:
        print("\nDNS proxy closed successfully")
