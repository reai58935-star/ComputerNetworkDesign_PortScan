from dataclasses import dataclass, field
from enum import Enum


class PortStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    ERROR = "error"


class HostStatus(Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class ScanResult:
    host: str
    port: int
    status: PortStatus
    service: str = "unknown"
    error_message: str = ""


@dataclass
class HostResult:
    host: str
    status: HostStatus
    open_ports: list[ScanResult] = field(default_factory=list)
    scan_time: float = 0.0
    error_message: str = ""


@dataclass
class ScanConfig:
    targets: list[str] = field(default_factory=list)
    ports: list[int] = field(default_factory=list)
    timeout: float = 1.0
    max_workers: int = 100
