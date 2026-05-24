# 架构设计

## 整体架构：分层 + 模块化

```
┌─────────────────────────────────┐
│       GUI (gui.py / gui.pyw)     │  ← tkinter 窗口，双击 gui.pyw 启动
│       CLI (cli.py)               │  ← argparse 子命令 scan / discover
├─────────────────────────────────┤
│       Scanner Engine             │
│  ┌───────────┐ ┌─────────────┐   │
│  │TCP Scanner│ │ICMP Scanner │   │  ← ThreadPoolExecutor 并发
│  │connect_ex │ │subprocess   │   │
│  │           │ │  ping       │   │
│  └───────────┘ └─────────────┘   │
│  ┌───────────────────────────┐   │
│  │  Utils (IP/Port parser,   │   │
│  │  300+ service names,      │   │  ← 工具 + 导出
│  │  JSON/CSV export)         │   │
│  ├───────────────────────────┤   │
│  │  Reporter (HTML/MD 报告)   │   │  ← 自动生成扫描报告
│  └───────────────────────────┘   │
├─────────────────────────────────┤
│    Python Standard Library       │
│  socket / threading / tkinter    │
│  ipaddress / subprocess / json   │
└─────────────────────────────────┘
```

## 模块职责

### `scanner/engine.py`
- `PortStatus` 枚举：OPEN / CLOSED / FILTERED / ERROR
- `HostStatus` 枚举：UP / DOWN / UNKNOWN
- `ScanResult` 数据类：单端口扫描结果 (host, port, status, service, error_message)
- `HostResult` 数据类：单主机扫描汇总 (host, status, open_ports, scan_time, error_message)
- `ScanConfig` 数据类：targets, ports, timeout, max_workers

### `scanner/tcp_scanner.py`
- `TCPScanner` 类：
  - `scan_port(host, port, timeout)` → `socket.connect_ex()` 单端口
  - `scan_host(host)` → ThreadPoolExecutor 并发扫端口，3 连续错误提前中止
  - `scan_network(on_result, on_progress)` → 串行遍历主机

### `scanner/icmp_scanner.py`
- `ICMPScanner` 类：
  - `ping(host)` → subprocess ping，自动适配 Win/Linux 参数
  - `discover_hosts(targets, on_result, on_progress)` → 并发 ping 发现存活主机

### `scanner/utils.py`
- `parse_ip_target(str)` → 支持单 IP / CIDR / IP 范围 / 域名
- `parse_port_range(str)` → 支持单端口 / 范围 / 逗号分隔 / 混合
- `SERVICE_NAMES` → 300+ 端口→服务名映射
- `get_service_name(port)` → 查服务名
- `export_json(results, filepath)` / `export_csv(results, filepath)`

### `scanner/reporter.py`
- `ReportGenerator` 类
- `generate_html(path)` — 内联 CSS 独立 HTML 报告
- `generate_markdown(path)` — Markdown 报告

### `cli.py`
- argparse 子命令：`scan` / `discover`
- 参数：`--target`, `--ports`, `--threads`, `--timeout`, `--output`, `--format`(json/csv/html/md)

### `gui.py`
- tkinter 窗口：黑客风暗色主题 (#0a0a0a / #00ff41)
- 输入：Target, Ports, Threads, Timeout
- 按钮：[SCAN] / [DISCOVER] / [STOP] / [EXPORT]
- 结果表格：只显示开放端口（closed/filtered 后台保存用于导出）
- 表格四列全部居中，只显示开放端口
- 后台 daemon 线程 + root.after() 跨线程更新

## 数据流
```
用户输入(CLI/GUI) → ScanConfig → TCPScanner/ICMPScanner
    → on_result 回调 → UI 更新表格
    → 完成后 ReportGenerator → 导出 HTML/MD/JSON/CSV
```
