#!/usr/bin/env python3

import socket
import os

# Path for the Unix socket file
socket_path = "/tmp/smart_house_socket"

# Simulated state of the house
house_state = {"temperature": 23.5, "lights": "on", "air_conditioning": "off"}


def start_socket_server():
    # Ensure no stale socket file exists
    if os.path.exists(socket_path):
        os.remove(socket_path)

    # Create a Unix domain socket
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(socket_path)
    server_socket.listen(1)

    print(f"Listening for connections on Unix socket {socket_path}...")

    while True:
        conn, addr = server_socket.accept()
        print("Connection established")

        # Send the current house state as bytes
        conn.sendall(str(house_state).encode("utf-8"))
        conn.close()


if __name__ == "__main__":
    start_socket_server()
