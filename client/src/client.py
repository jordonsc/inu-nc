#!/usr/bin/env python3

import select
import socket
import argparse
import threading
import sys

from exceptions import *


class Client:
    NET_BUFFER_SIZE = 1024

    def __init__(self):
        """Initialize the client with default settings."""
        self.stop_event = threading.Event()



    def shell(self, reader, writer):
        """
        Handle the client shell for reading from and writing to the server.

        Args:
            reader (socket): The reader socket.
            writer (socket): The writer socket.
        """
        def read_from_server():
            # Listen for server messages until the stop event is set from another thread
            while not self.stop_event.is_set():
                try:
                    outp = reader.recv(self.NET_BUFFER_SIZE)
                    if not outp:
                        print("Server closed the connection.")
                        break
                    message = outp.decode().strip()
                    self.handle_message(message)
                except ServerTerminatedConnectionError as e:
                    print(f"Server closed the connection.")
                    break
                except Exception as e:
                    print(f"Read error: {e}")
                    break
                
            self.stop_event.set()

        def write_to_server():
            # Buffer for user input
            buffer = b''

            # Listen for user input until the stop event is set from another thread
            while not self.stop_event.is_set():
                try:
                    # Check if there is any data on stdin
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        user_input = sys.stdin.buffer.raw.read(1)
                        buffer += user_input

                        # Send command on new-line, including the line-break
                        if user_input == b'\n':
                            writer.sendall(buffer)
                            buffer = b''
                    else:
                        continue

                except Exception as e:
                    print(f"Write error: {e}")
                    break

            self.stop_event.set()

        read_thread = threading.Thread(target=read_from_server)
        write_thread = threading.Thread(target=write_to_server)

        read_thread.start()
        write_thread.start()

        read_thread.join()
        write_thread.join()

        writer.close()
        reader.close()

    def handle_message(self, message):
        """
        Handle a message from the server.

        Args:
            message (str): The message from the server.
        """
        # Check for an embedded message in the format [MSG:...]
        if message.startswith("[MSG:") and message.endswith("]"):
            note = message[5:-1]
            if note == "Exit":
                raise ServerTerminatedConnectionError("Server terminated the connection.")

            print(f"Message: {note}", flush=True)
            return

        # Otherwise, print the message as-is
        print(message, flush=True)

    def connect(self, host='localhost', port=23):
        """
        Connect to the server and start the shell.

        Args:
            host (str): The server host. Defaults to 'localhost'.
            port (int): The server port. Defaults to 23.
        """
        try:
            reader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            reader.connect((host, port))
            writer = reader
            self.shell(reader, writer)
        except ConnectionRefusedError:
            print("Connection refused. Please check the server address and port.")
        except socket.timeout:
            print("Connection timed out.")
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print("Connection reset by peer.")
        except ServerTerminatedConnectionError:
            print("Server terminated the connection.")
        except Exception as e:
            print(f"Unknown error ({type(e).__name__}): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inu-NC Client")
    parser.add_argument('-i', '--host', type=str, default='localhost', help='Server host')
    parser.add_argument('-p', '--port', type=int, default=23, help='Server port')
    args = parser.parse_args()

    client = Client()
    try:
        client.connect(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting..")
        client.stop_event.set()
    