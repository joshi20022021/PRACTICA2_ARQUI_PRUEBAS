#!/usr/bin/env python3

import socket
import os
import json

from states import SmartHomeState

# Path for the Unix socket file
STATE_SOCKET_PATH = "/tmp/smart_house_state_socket"
COMMAND_SOCKET_PATH = "/tmp/smart_house_command_socket"


def handle_state_socket(house_state: SmartHomeState):
    """This function handles the state socket."""
    if os.path.exists(STATE_SOCKET_PATH):
        os.remove(STATE_SOCKET_PATH)

    # Create a Unix domain socket for state retrieval
    state_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    state_socket.bind(STATE_SOCKET_PATH)
    state_socket.listen(1)
    print(f"Listening for house state on Unix socket {STATE_SOCKET_PATH}...")

    while True:
        conn, _ = state_socket.accept()
        print("State connection established")

        new_house_state = house_state.to_dict()
        conn.sendall(str(new_house_state).encode("utf-8"))
        # conn.sendall(json.dumps(house_state).encode("utf-8"))
        # conn.sendall(str(house_state).encode("utf-8"))  # Send house state as bytes
        conn.close()
        print("Get state Connection closed")


def handle_command_socket(house_state: SmartHomeState):
    """This function handles the command socket."""
    if os.path.exists(COMMAND_SOCKET_PATH):
        os.remove(COMMAND_SOCKET_PATH)

    # Create a Unix domain socket for command processing
    command_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    command_socket.bind(COMMAND_SOCKET_PATH)
    command_socket.listen(1)
    print(f"Listening for commands on Unix socket {COMMAND_SOCKET_PATH}...")

    while True:
        conn, _ = command_socket.accept()
        data = conn.recv(1024)
        if data:
            command = eval(data.decode("utf-8"))
            # Handle commands like toggling lights
            match command.get("command"):
                case "toggle_lights":
                    new_light_state = command.get("state")
                    house_state.light = new_light_state
                case "toggle_alarm":
                    new_alarm_state = command.get("state")
                    house_state.alarm = new_alarm_state
                case "toggle_greenhouse":
                    new_greenhouse_state = command.get("state")
                    house_state.water_pump = new_greenhouse_state
                case "send_message":
                    new_message = command.get("message")
                    house_state.message = new_message
        try:
            new_house_state = house_state.to_dict()
            conn.sendall(str(new_house_state).encode("utf-8"))
        except BrokenPipeError:
            print("Client closed")
        conn.close()


if __name__ == "__main__":
    # Run the two socket handlers in parallel (you can use threading)
    from threading import Thread

    state_thread = Thread(target=handle_state_socket)
    command_thread = Thread(target=handle_command_socket)
    state_thread.start()
    command_thread.start()

    state_thread.join()
    command_thread.join()
    os.remove(STATE_SOCKET_PATH)
    os.remove(COMMAND_SOCKET_PATH)
