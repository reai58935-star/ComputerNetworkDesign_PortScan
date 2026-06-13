# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
A cross-platform port scanner built with Python's standard library for a university course design project. Uses TCP connect for port scanning and ICMP echo for host discovery, with both CLI and GUI interfaces, plus auto-generated HTML/Markdown scan reports.

## Commands
```bash
# Run port scan via CLI
python cli.py scan --target 127.0.0.1 --ports 1-1024 --threads 100 --timeout 1.0

# Run host discovery via CLI
python cli.py discover --network 192.168.1.0/24 --threads 50

# Export scan report (HTML/MD/JSON/CSV)
python cli.py scan --target 127.0.0.1 --ports 1-1024 --output report.html --format html

# Run GUI (no console — double-click in File Explorer)
gui.pyw              # double-click to launch without cmd window

# Run GUI with console visible (debugging)
python gui.py

# Run all tests
python -m unittest discover tests/ -v

# Run a single test file
python -m unittest tests.test_utils
python -m unittest tests.test_scanner
```

## Architecture
Four-layer design with strict one-way dependency:

```
CLI (cli.py) / GUI (gui.py)    ← Presentation layer; scanner/ must NOT import these
        │
Scanner Engine (scanner/)       ← Business logic; no print(), no direct UI coupling
  ├── engine.py:  ScanResult, HostResult, ScanConfig dataclasses, PortStatus/HostStatus enums
  ├── tcp_scanner.py: TCPScanner — TCP connect() scan, ThreadPoolExecutor, early abort at 3 errors
  ├── icmp_scanner.py: ICMPScanner — ICMP echo via subprocess ping, auto-detect Win/Linux
  ├── utils.py: parse_ip_target, parse_port_range, SERVICE_NAMES (1023/1023 全网端口 1-1023 全覆盖 + 注册/高端口), export_json/csv
  └── reporter.py: ReportGenerator — generate_html() and generate_markdown() reports
        │
Python stdlib (socket, threading, ipaddress, tkinter, subprocess, argparse) ← Zero dependencies
```

## Core Constraints
- **Zero external dependencies** — standard library only; never add pip packages
- **Engine never prints** — `scanner/` modules return results via dataclass objects. CLI/GUI handle all display.
- **GUI runs scan in background thread** — `daemon=True` thread, uses `root.after()` for cross-thread UI updates
- **TCP connect only** — `socket.connect_ex()`, no raw sockets, no admin/root required
- **ICMP via subprocess ping** — auto-detects Windows (`ping -n 1 -w <ms>`) vs Linux (`ping -c 1 -W <sec>`)
- **Cross-platform** — all socket code works on Windows and Linux without platform-specific imports

## GUI Design
- **Hacker theme**: dark background (#0a0a0a), green text (#00ff41), cyan (#00ffff)
- **Scan results show only open ports** in the table; closed/filtered results saved internally for export
- **gui.pyw**: double-click launcher, no console window, Windows associates .pyw with pythonw.exe automatically
- Progress bar, thread/timeout inputs, terminal-style input prompts (`Target >`, `Ports >`)
- All four table columns (HOST, PORT, STATUS, SERVICE) center-aligned

## Type Hints
All functions must include parameter and return type annotations. Dataclasses in `engine.py` define the data contract.

## Course Design Report (gen_report.js)
- `gen_report.js` — Node.js script using `docx` library to auto-generate `课程设计报告.docx`
- Requires `npm install docx` before first use, then `node gen_report.js` to regenerate
- `node_modules/` is gitignored; `package.json` and `package-lock.json` are committed
