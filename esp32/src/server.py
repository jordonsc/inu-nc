import argparse
import asyncio
import logging

from error_codes import ErrorCodes
from exceptions import GCodeException
from gcode import GCodeParser


class Server:
    SERVER_NAME = "Inu-NC"
    SERVER_VERSION = "1.0"
    NET_BUFFER_SIZE = 1024

    def __init__(self):
        """Initialize the server with default settings."""
        self.connections = set()
        self.logger = logging.getLogger("INU.SERVER")
        logging.basicConfig(level=logging.INFO)
        self.max_connections = 5

    async def handle_client(self, reader, writer):
        """
        Handle a new client connection.

        Args:
            reader (StreamReader): The reader stream.
            writer (StreamWriter): The writer stream.
        """
        addr = writer.get_extra_info('peername')

        # Reject the connection if the maximum number of connections is reached
        if len(self.connections) >= self.max_connections:
            self.logger.info(f"Rejecting connection from {addr}: too many connections")
            writer.write(ErrorCodes.fmt(ErrorCodes.TOO_MANY_CONNECTIONS).encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        # Accept the connection and add to connection pool
        self.logger.info(f"New connection from {addr}")
        self.connections.add(writer)

        writer.write(f"Connected: {self.SERVER_NAME} {self.SERVER_VERSION}\n".encode())

        try:
            # Indefinitely read data from the client
            while True:
                data = await reader.read(self.NET_BUFFER_SIZE)
                if not data:
                    break
                message = data.decode()
                self.logger.info(f"{addr}:")

                # Parse the message as G-code
                try:
                    parsed_commands = GCodeParser.parse(message)
                    for cmd in parsed_commands:
                        self.logger.info(f" - {cmd}")

                    writer.write("ok\n".encode())
                except GCodeException as e:
                    self.logger.error(f"GCode error: {e}")
                    writer.write(ErrorCodes.fmt(e.error_code).encode())

                await writer.drain()

        except Exception as e:
            self.logger.error(f"Client error ({type(e).__name__}): {e}")

        finally:
            self.logger.info(f"Closing connection from {addr}")
            self.connections.remove(writer)
            writer.close()
            await writer.wait_closed()

    async def run(self, host='0.0.0.0', port=23, max_connections=None):
        """
        Asynchronously runs the server.

        Args:
            host (str): The hostname to listen on. Defaults to '0.0.0.0'.
            port (int): The port to listen on. Defaults to 23.
            max_connections (int, optional): The maximum number of simultaneous connections. Defaults to None.

        Raises:
            KeyboardInterrupt: If the server is interrupted by a keyboard interrupt.
        """
        if max_connections is not None:
            self.max_connections = max_connections

        try:
            server = await asyncio.start_server(self.handle_client, host, port)
            addr = server.sockets[0].getsockname()
            self.logger.info(f"Serving on {addr}")

            async with server:
                await server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt, exiting..")
        finally:
            await self.broadcast_message("Exit")

    async def broadcast_message(self, message):
        """
        Broadcast a [MSG:....] message to all connected clients.
        """
        await self.broadcast(f"[MSG:{message}]")

    async def broadcast(self, message):
        """
        Broadcast a generic message to all connected clients.

        Args:
            message (str): The message to send.
        """
        for writer in self.connections:
            print(f"Sending to {writer.get_extra_info('peername')}: {message}")
            writer.write(f"{message}\n".encode())
            await writer.drain()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inu-NC Client")
    parser.add_argument('-i', '--host', type=str, default='localhost', help='Server host')
    parser.add_argument('-p', '--port', type=int, default=23, help='Server port')
    parser.add_argument('-m', '--connections', type=int, default=5, help='Max client connections')
    args = parser.parse_args()

    server = Server()
    try:
        asyncio.run(server.run(args.host, args.port, args.connections))
    except KeyboardInterrupt:
        server.logger.info("Server interrupted. Exiting...")
