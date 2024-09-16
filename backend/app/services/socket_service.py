#!/usr/bin/env python3

import socket


state_socket_path = "/tmp/smart_house_state_socket"
command_socket_path = "/tmp/smart_house_command_socket"


def get_house_state_from_socket():
    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(state_socket_path)
        data = s.recv(1024)  # Receive data from the socket (1024 bytes)

    # Decode the received data and convert it to a dictionary
    house_state = eval(
        data.decode("utf-8")
    )  # Be cautious with eval; JSON is preferred in production
    return house_state


def send_light_command_to_socket(new_light_state):
    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(command_socket_path)
        command = {"command": "toggle_lights", "state": new_light_state}
        s.sendall(
            str(command).encode("utf-8")
        )  # Send the new light state to the control program
        # Receive the updated house state after the command is executed
        data = s.recv(1024)
        return eval(data.decode("utf-8"))


def send_alarm_command_to_socket(new_alarm_state):
    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(command_socket_path)
        command = {"command": "toggle_alarm", "state": new_alarm_state}
        s.sendall(
            str(command).encode("utf-8")
        )  # Send the new light state to the control program
        # Receive the updated house state after the command is executed
        data = s.recv(1024)
        return eval(data.decode("utf-8"))


def send_greenhouse_command_to_socket(new_greenhouse_state):
    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(command_socket_path)
        command = {"command": "toggle_greenhouse", "state": new_greenhouse_state}
        s.sendall(
            str(command).encode("utf-8")
        )  # Send the new light state to the control program
        # Receive the updated house state after the command is executed
        data = s.recv(1024)
        return eval(data.decode("utf-8"))


def send_message_to_socket(message):
    # Create a Unix socket and connect to the socket file
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(command_socket_path)
        command = {"command": "send_message", "message": message}
        s.sendall(
            str(command).encode("utf-8")
        )  # Send the new light state to the control program
        # Receive the updated house state after the command is executed
        data = s.recv(1024)
        return eval(data.decode("utf-8"))
