import csv
import json
import socket
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from scanner.engine import HostResult

SERVICE_NAMES: dict[int, str] = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet",
    25: "smtp", 53: "dns", 80: "http", 110: "pop3",
    143: "imap", 443: "https", 993: "imaps", 995: "pop3s",
    3306: "mysql", 3389: "rdp", 5432: "postgresql",
    6379: "redis", 8080: "http-proxy", 8443: "https-alt",
    27017: "mongodb",
}


def get_service_name(port: int) -> str:
    return SERVICE_NAMES.get(port, "unknown")


def parse_ip_target(target: str) -> list[str]:
    target = target.strip()
    if not target:
        raise ValueError("Empty target")

    # CIDR notation: 192.168.1.0/24
    if "/" in target:
        try:
            network = IPv4Network(target, strict=False)
            return [str(host) for host in network.hosts()]
        except (AddressValueError, ValueError) as e:
            raise ValueError(f"Invalid CIDR target '{target}': {e}") from e

    # Range notation: 192.168.1.1-192.168.1.10
    if "-" in target:
        parts = target.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid IP range '{target}': expected 'start-end'")
        try:
            start = IPv4Address(parts[0].strip())
            end = IPv4Address(parts[1].strip())
        except AddressValueError as e:
            raise ValueError(f"Invalid IP in range '{target}': {e}") from e
        if start > end:
            raise ValueError(f"Invalid range '{target}': start > end")
        return [str(IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]

    # Single IP or hostname
    return [target]


def parse_port_range(port_str: str) -> list[int]:
    port_str = port_str.strip()
    if not port_str:
        raise ValueError("Empty port specification")

    ports: list[int] = []
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            range_parts = part.split("-")
            if len(range_parts) != 2:
                raise ValueError(f"Invalid port range '{part}': expected 'start-end'")
            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
            except ValueError as e:
                raise ValueError(f"Invalid port number in '{part}': {e}") from e
            if start > end:
                raise ValueError(f"Invalid port range '{part}': start > end")
            if start < 1 or end > 65535:
                raise ValueError(f"Ports must be 1-65535, got '{part}'")
            ports.extend(range(start, end + 1))
        else:
            try:
                port = int(part)
            except ValueError as e:
                raise ValueError(f"Invalid port '{part}': {e}") from e
            if port < 1 or port > 65535:
                raise ValueError(f"Port must be 1-65535, got {port}")
            ports.append(port)

    if not ports:
        raise ValueError("No ports specified")
    return ports


def export_json(results: list[HostResult], filepath: str) -> None:
    data = []
    for host in results:
        data.append({
            "host": host.host,
            "status": host.status.value,
            "scan_time": host.scan_time,
            "error_message": host.error_message,
            "open_ports": [
                {
                    "port": r.port,
                    "service": r.service,
                    "error_message": r.error_message,
                }
                for r in host.open_ports
            ],
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_csv(results: list[HostResult], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["host", "port", "status", "service", "error_message"])
        for host in results:
            if host.open_ports:
                for r in host.open_ports:
                    writer.writerow([r.host, r.port, r.status.value, r.service, r.error_message])
            else:
                writer.writerow([host.host, "", host.status.value, "", host.error_message])
