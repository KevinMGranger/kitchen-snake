"""
A bare simple HTTP server, merely for testing.
"""


import contextlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from ssl import SSLContext, SSLSocket
from threading import Thread

DEFAULT_ADDR = "127.0.0.1"
DEFAULT_PORT = 0  # random port
DEFAULT_RESPONSE_TEXT = b"Hello, world!"

# TODO: logging?


def make_server(
    address: str = DEFAULT_ADDR,
    port: int = DEFAULT_PORT,
    ssl_context: SSLContext | None = None,
    response_text: bytes = DEFAULT_RESPONSE_TEXT,
) -> HTTPServer:
    """
    Create a simple HTTP(s) server that responds to all requests with
    the given response_text.
    """

    class _ResponseHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200, "ALL GOOD")
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(response_text)))
            self.end_headers()
            self.wfile.write(response_text)

    server = HTTPServer(
        (address, port), _ResponseHandler
    )  # TODO: will listen work with ipv6?
    if ssl_context is not None:
        # why isn't this documented? :/
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)  # type: ignore
    return server


class Server:
    """
    A server and an associated thread.
    """

    def __init__(self, server: HTTPServer, threader: type[Thread] = Thread):
        self.server = server
        self.thread = threader(target=server.serve_forever)

    @property
    def protocol(self) -> str:
        "HTTP or HTTPS?"
        if isinstance(self.server.socket, SSLSocket):
            return "https"
        else:
            return "http"

    @property
    def address(self) -> str:
        return self.server.socket.getsockname()[0]

    @property
    def port(self) -> int:
        return self.server.server_port

    @property
    def url(self) -> str:
        "The base URL that the server is reachable by."
        return f"{self.protocol}://{self.address}:{self.port}/"

    def start(self):
        "Start the server thread."
        self.thread.start()

    @contextlib.contextmanager
    def serve(self):
        self.thread.start()
        yield self
        self.wait()  # TODO: what if caller stops it?

    def wait(self):
        "wait for the thread"
        try:
            self.thread.join()
        except KeyboardInterrupt:
            print("\nShutting down server")
            self.stop()

    def stop(self):
        "Stop the server, waiting for shutdown."
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def __str__(self):
        return f"{self.protocol} serving at {self.url}"


try:
    import click

    from kmg.kitchen.ip import IPAddress, ListenSpec

    @click.command()
    @click.option("--response", default=DEFAULT_RESPONSE_TEXT)
    @click.argument(
        "listen_address",
        type=ListenSpec(DEFAULT_ADDR, DEFAULT_PORT),
        default=(DEFAULT_ADDR, DEFAULT_PORT),
    )
    def _serve(response: str, listen_address: tuple[IPAddress, int]):
        addr, port = listen_address
        server = Server(make_server(str(addr), port, response_text=response.encode()))

        with server.serve():
            print("Serving at", click.style(server.url, bold=True))

    if __name__ == "__main__":
        _serve()

except NameError:
    pass
