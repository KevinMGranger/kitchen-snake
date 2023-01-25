import ipaddress
import re
from ipaddress import IPv4Address, IPv6Address
from typing import Any, ClassVar, TypeAlias

import click

from .python import Unreachable

IPAddress: TypeAlias = IPv4Address | IPv6Address


class ListenSpec(click.ParamType):
    """
    Parse an ip address specification (IP:PORT).
    ipv4 requires the standard dot notation.
    Defaults for both can be given.
    If a part is ommitted without a default, an error is raised.
    If just a decimal number is given, it is assumed to be a port.
    """

    name: ClassVar[str] = "IP and Port"
    V6_WITH_PORT_REGEX: ClassVar[re.Pattern] = re.compile(r"\[(.*)]:(\d+)")
    V4_WITH_PORT_REGEX: ClassVar[re.Pattern] = re.compile(r"(\d+\.\d+\.\d+\.\d):(\d+)")

    default_addr: IPAddress | None
    default_port: int | None

    def __init__(
        self,
        default_addr: str | IPAddress | None = None,
        default_port: int | None = None,
    ):
        self.default_addr = (
            ipaddress.ip_address(default_addr)
            if isinstance(default_addr, str)
            else default_addr
        )
        self.default_port = default_port

    def _convert_port(self, value: str) -> int | None:
        try:  # just a port?
            port = int(value)
            if port >= 2**16:  # TODO: does ipv6 have bigger ports?
                self.fail(f"invalid port value: {port}")
            return port
        except ValueError:
            return None

    def _convert_str(self, value: str) -> tuple[IPv4Address | IPv6Address, int]:
        # just a port?
        port = self._convert_port(value)
        match self.default_addr, port:
            case _, None:
                pass
            case None, int():
                self.fail(f"Got port {port} but need an address too")
            case IPv4Address() | IPv6Address() as addr, int() as port:
                return addr, port
            case _, _:
                raise Unreachable

        if (match := self.V6_WITH_PORT_REGEX.match(value)) is not None:
            addr = ipaddress.IPv6Address(match.group(1))
            port = int(match.group(2))
            return addr, port

        if (match := self.V4_WITH_PORT_REGEX.match(value)) is not None:
            addr = ipaddress.IPv4Address(match.group(1))
            port = int(match.group(2))
            return addr, port

        # just an IP
        addr = ipaddress.ip_address(value)

        if self.default_port is None:
            self.fail(f"got just an IP {addr} but no default port was set")

        return addr, self.default_port

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> tuple[IPv4Address | IPv6Address, int]:
        match value:
            case (str() | IPv4Address() | IPv6Address() as addr, int() as port):
                return ipaddress.ip_address(addr), port
            case str():
                return self._convert_str(value)
            case _:
                self.fail(f"Unknown type for conversion: got a {value}")
