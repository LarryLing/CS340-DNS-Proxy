import socket

PORT = 53
SERVER_IP = "8.8.8.8"
ADDR = (SERVER_IP, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDR)
