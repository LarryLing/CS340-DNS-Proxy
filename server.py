import socket

PORT = 1053
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)

proxy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
proxy.bind(ADDR)

proxyMessage, proxyAddress = proxy.recvfrom(2048)
print(f"received {proxyMessage} from {proxyAddress}")

upstream_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

upstream_resolver.sendto(proxyMessage, ("8.8.8.8", 53))
resolverMessage, resolverAddress = upstream_resolver.recvfrom(2048)
print(f"received {resolverMessage} from {resolverAddress}")

proxy.sendto(resolverMessage, proxyAddress)
