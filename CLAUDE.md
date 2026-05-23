# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
A cross-platform port scanner built with Python's standard library for a university course design project. Uses TCP connect for port scanning and ICMP echo for host discovery, with both CLI and GUI interfaces.

## Commands
```bash
# Run port scan via CLI
python cli.py scan --host 192.168.1.0/24 --ports 1-1024 --threads 100

# Run host discovery via CLI
python cli.py discover --network 192.168.1.0/24

# Run GUI
python gui.py

# Run all tests
python -m unittest discover tests/

# Run a single test
python -m unittest tests.test_scanner
```

## Architecture
Three-layer design with strict separation:

```
CLI (cli.py) / GUI (gui.py)   ← Presentation layer; must NOT be imported by scanner/
        │
Scanner Engine (scanner/)     ← Business logic; no print(), no UI coupling
  ├── engine.py: ScanResult, HostResult, ScanConfig dataclasses
  ├── tcp_scanner.py: TCPScanner — TCP connect scan with threading
  ├── icmp_scanner.py: ICMPScanner — ICMP echo host discovery
  └── utils.py: IP/port parsing, service name lookup, JSON/CSV export
        │
Python stdlib (socket, threading, ipaddress)   ← Zero external dependencies
```

## Core Constraints
- **Zero external dependencies** — standard library only; never add pip packages
- **Engine never prints** — `scanner/` modules return results via dataclass objects, never call `print()`. UI layers handle all display.
- **GUI runs scan in background thread** — `gui.py` must use `threading.Thread` for scan execution to keep UI responsive
- **TCP connect only** — no raw sockets, no admin/root required, full cross-platform
- **Cross-platform** — all socket code must work on both Windows and Linux without platform-specific paths

## Type Hints
All functions must include parameter and return type annotations. Dataclasses in `engine.py` define the data contract between scanner and UI layers.
