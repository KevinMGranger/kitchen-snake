import webbrowser
from pathlib import Path
from ssl import PROTOCOL_TLS_SERVER, SSLContext

from . import http
from .http import DEFAULT_ADDR, DEFAULT_PORT, Server

DEFAULT_RESPONSE_TEXT = b"Secure hello,  world!"


def make_context(bundle: Path | str, keyfile: Path | str) -> SSLContext:
    "Make an SSL context with the right protocol and given bundle / key info"
    ctx = SSLContext(PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(bundle, keyfile)
    return ctx


def make_server(
    address: str,
    port: int,
    ssl_context: SSLContext,
    response_text: bytes = DEFAULT_RESPONSE_TEXT,
):
    """
    Create a simple HTTPs server that responds to all requests with
    the given response_text.
    """
    return http.make_server(address, port, ssl_context, response_text)


try:
    import click

    from kmg.kitchen.ip import IPAddress, ListenSpec

    @click.command()
    @click.option(
        "-p",
        "--privkey",
        required=True,
        type=click.Path(exists=True, readable=True),
        help="The leaf cert private key",
    )
    @click.option(
        "--certs",
        required=True,
        type=click.Path(exists=True, readable=True),
        help="The certificate bundle",
    )
    @click.option(
        "--browser",
        default=False,
        is_flag=True,
        show_default=True,
        help="Launch a browser pointed at the running server",
    )
    @click.option("--response", default=DEFAULT_RESPONSE_TEXT)
    @click.argument(
        "listen_address",
        type=ListenSpec(DEFAULT_ADDR, DEFAULT_PORT),
        default=(DEFAULT_ADDR, DEFAULT_PORT),
    )
    def _serve(
        privkey: str,
        certs: str,
        response: str,
        browser: bool,
        listen_address: tuple[IPAddress, int],
    ):
        ctx = make_context(certs, privkey)

        addr, port = listen_address
        server = Server(
            make_server(
                str(addr), port, ssl_context=ctx, response_text=response.encode()
            )
        )

        with server.serve():
            print("Serving at", click.style(server.url, bold=True))
            if browser:
                webbrowser.open(server.url)

    if __name__ == "__main__":
        _serve()

except NameError:
    pass
