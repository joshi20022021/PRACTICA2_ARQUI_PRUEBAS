#!/usr/bin/env python3

import socket
import os

# Path for the Unix socket file
state_socket_path = "/tmp/smart_house_state_socket"
command_socket_path = "/tmp/smart_house_command_socket"

# Simulated state of the house
house_state = {"temperature": 23.5, "lights": "on", "air_conditioning": "off"}


def handle_state_socket():
    """This function handles the state socket."""
    if os.path.exists(state_socket_path):
        os.remove(state_socket_path)

    # Create a Unix domain socket for state retrieval
    state_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    state_socket.bind(state_socket_path)
    state_socket.listen(1)
    print(f"Listening for house state on Unix socket {state_socket_path}...")

    while True:
        conn, _ = state_socket.accept()
        print("State connection established")
        conn.sendall(str(house_state).encode("utf-8"))  # Send house state as bytes
        conn.close()


def handle_command_socket():
    """This function handles the command socket."""
    if os.path.exists(command_socket_path):
        os.remove(command_socket_path)

    # Create a Unix domain socket for command processing
    command_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    command_socket.bind(command_socket_path)
    command_socket.listen(1)
    print(f"Listening for commands on Unix socket {command_socket_path}...")

    while True:
        conn, _ = command_socket.accept()
        print("Command connection established")
        data = conn.recv(1024)
        if data:
            command = eval(data.decode("utf-8"))
            # Handle commands like toggling lights
            match command.get("command"):
                case "toggle_lights":
                    new_light_state = command.get("state")
                    house_state["lights"] = new_light_state
                    print(f"Lights have been toggled to: {new_light_state}")

        conn.sendall(str(house_state).encode("utf-8"))  # Send updated state back
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
    os.remove(state_socket_path)
    os.remove(command_socket_path)
