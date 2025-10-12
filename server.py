import socket

from constants import LOCAL_IP, LOCAL_PORT, RESOLVER_IP, RESOLVER_PORT
from log import log_data

proxy_address = (LOCAL_IP, LOCAL_PORT)
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
proxy_socket.bind(proxy_address)

resolver_address = (RESOLVER_IP, RESOLVER_PORT)
resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
resolver_socket.settimeout(5.0)

try:
    while True:
        proxy_message, client_address = proxy_socket.recvfrom(2048)
        log_data(proxy_address, proxy_message)

        resolver_message = None

        for tries in range(3):
            try:
                resolver_socket.sendto(proxy_message, (RESOLVER_IP, RESOLVER_PORT))
                resolver_message, _ = resolver_socket.recvfrom(2048)
                break
            except socket.timeout:
                print(
                    f"Timeout waiting for response from {resolver_address} (Attempt {tries + 1}/3)"
                )
            except socket.error as e:
                print(
                    f"An error occurred while communicating with upstream resolver: {e} (Attempt {tries + 1}/3)"
                )

        if resolver_message:
            log_data(resolver_address, resolver_message)
            proxy_socket.sendto(resolver_message, client_address)
        else:
            print("Failed to communicate with upstream resolver")

except KeyboardInterrupt:
    print("\nClosing sockets...")

except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")

finally:
    proxy_socket.close()
    resolver_socket.close()
    print("DNS proxy stopped successfully")
