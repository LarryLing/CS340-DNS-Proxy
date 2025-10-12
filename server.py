import socket

from constants import LOCAL_IP, LOCAL_PORT, RESOLVER_IP, RESOLVER_PORT
from log import log_data

proxy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
proxy.bind((LOCAL_IP, LOCAL_PORT))

proxyMessage, proxyAddress = proxy.recvfrom(2048)
log_data(proxyAddress, proxyMessage)

upstream_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

upstream_resolver.sendto(proxyMessage, (RESOLVER_IP, RESOLVER_PORT))
resolverMessage, resolverAddress = upstream_resolver.recvfrom(2048)
log_data(resolverAddress, resolverMessage)

proxy.sendto(resolverMessage, proxyAddress)
