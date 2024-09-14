#!/usr/bin/env python3

import socket


def get_house_state_from_socket():
    socket_path = "/tmp/smart_house_socket"  # Path to the Unix socket file

    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        data = s.recv(1024)  # Receive data from the socket (1024 bytes)

    # Decode the received data and convert it to a dictionary
    house_state = eval(
        data.decode("utf-8")
    )  # Be cautious with eval; JSON is preferred in production
    return house_state
