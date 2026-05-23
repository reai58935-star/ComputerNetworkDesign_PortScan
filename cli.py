import argparse
import sys
from scanner import (
    TCPScanner, ICMPScanner, ScanConfig,
    parse_ip_target, parse_port_range,
    export_json, export_csv, ReportGenerator,
)


def cmd_scan(args: argparse.Namespace) -> None:
    try:
        targets = parse_ip_target(args.target)
        ports = parse_port_range(args.ports)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Targets: {len(targets)} host(s)")
    print(f"Ports: {len(ports)} port(s)")
    print(f"Threads: {args.threads}, Timeout: {args.timeout}s")
    print("-" * 50)

    config = ScanConfig(
        targets=targets, ports=ports,
        timeout=args.timeout, max_workers=args.threads,
    )
    scanner = TCPScanner(config)

    def on_result(result) -> None:
        if result.status.value == "open":
            print(f"  [OPEN] {result.host}:{result.port} ({result.service})")

    def on_progress(done: int, total: int) -> None:
        pct = done / total * 100
        print(f"\rProgress: {done}/{total} hosts ({pct:.1f}%)", end="", flush=True)

    results = scanner.scan_network(on_result=on_result, on_progress=on_progress)
    print()  # newline after progress

    open_total = sum(len(h.open_ports) for h in results)
    hosts_up = sum(1 for h in results if h.status.value == "up")
    print("-" * 50)
    print(f"Done. {hosts_up} host(s) up, {open_total} open port(s) found.")

    _handle_output(results, config, args)


def cmd_discover(args: argparse.Namespace) -> None:
    try:
        targets = parse_ip_target(args.network)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Discovering {len(targets)} host(s)...")
    print("-" * 50)

    scanner = ICMPScanner(timeout=args.timeout, max_workers=args.threads)

    def on_result(result) -> None:
        if result.status.value == "up":
            print(f"  [UP] {result.host}")

    def on_progress(done: int, total: int) -> None:
        pct = done / total * 100
        print(f"\rProgress: {done}/{total} ({pct:.1f}%)", end="", flush=True)

    results = scanner.discover_hosts(
        targets, on_result=on_result, on_progress=on_progress,
    )
    print()

    hosts_up = sum(1 for h in results if h.status.value == "up")
    print("-" * 50)
    print(f"Done. {hosts_up}/{len(targets)} host(s) up.")

    _handle_output(results, ScanConfig(targets=targets, ports=[]), args)


def _handle_output(results, config, args) -> None:
    if not args.output:
        return
    fmt = args.format
    if fmt == "json":
        export_json(results, args.output)
    elif fmt == "csv":
        export_csv(results, args.output)
    elif fmt == "html":
        ReportGenerator(results, config).generate_html(args.output)
    elif fmt == "md":
        ReportGenerator(results, config).generate_markdown(args.output)
    print(f"Report saved: {args.output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="portscanner",
        description="Cross-platform TCP port scanner and ICMP host discovery tool",
    )
    sub = parser.add_subparsers(dest="command")

    # scan subcommand
    p_scan = sub.add_parser("scan", help="TCP connect port scan")
    p_scan.add_argument("--target", "-t", required=True, help="IP, CIDR, range, or hostname")
    p_scan.add_argument("--ports", "-p", default="1-1024", help="Port range (default: 1-1024)")
    p_scan.add_argument("--threads", type=int, default=100, help="Max concurrent threads (default: 100)")
    p_scan.add_argument("--timeout", type=float, default=1.0, help="Per-socket timeout in seconds (default: 1.0)")
    p_scan.add_argument("--output", "-o", help="Output file path")
    p_scan.add_argument("--format", "-f", choices=["json", "csv", "html", "md"], default="html", help="Output format (default: html)")

    # discover subcommand
    p_disc = sub.add_parser("discover", help="ICMP host discovery")
    p_disc.add_argument("--network", "-n", required=True, help="Network CIDR or IP range")
    p_disc.add_argument("--threads", type=int, default=50, help="Max concurrent pings (default: 50)")
    p_disc.add_argument("--timeout", type=float, default=1.0, help="Ping timeout in seconds (default: 1.0)")
    p_disc.add_argument("--output", "-o", help="Output file path")
    p_disc.add_argument("--format", "-f", choices=["json", "csv", "html", "md"], default="html", help="Output format (default: html)")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "discover":
        cmd_discover(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
