# 架构设计

## 整体架构：分层 + 模块化

```
┌─────────────────────────────────┐
│          GUI (gui.py)            │  ← tkinter 窗口界面
│          CLI (cli.py)            │  ← argparse 命令行
├─────────────────────────────────┤
│       Scanner Engine             │
│  ┌───────────┐ ┌─────────────┐   │
│  │TCP Scanner│ │ICMP Scanner │   │  ← 核心扫描引擎
│  └───────────┘ └─────────────┘   │
│  ┌───────────────────────────┐   │
│  │     Utils (IP parser,     │   │
│  │     result formatter)     │   │  ← 工具层
│  └───────────────────────────┘   │
├─────────────────────────────────┤
│       Python Standard Library    │
│   socket / threading / ipaddress │
└─────────────────────────────────┘
```

## 模块职责

### `scanner/__init__.py`
包初始化，导出公共接口

### `scanner/engine.py`
- `ScanResult` 数据类：单个端口扫描结果（host, port, status, service）
- `HostResult` 数据类：单主机扫描结果汇总
- `ScanConfig` 数据类：扫描配置（IP范围、端口范围、线程数、超时）

### `scanner/tcp_scanner.py`
- `TCPScanner` 类：
  - `scan_port(host, port, timeout)` → 单端口 TCP connect 扫描
  - `scan_host(config)` → 扫描单个主机的端口范围（多线程）
  - `scan_network(config)` → 扫描整个网段

### `scanner/icmp_scanner.py`
- `ICMPScanner` 类：
  - `ping(host, timeout)` → 单主机 ICMP echo 检测
  - `discover_hosts(network)` → 网段内存活主机发现

### `scanner/utils.py`
- `parse_ip_range(ip_str)` → 解析 "192.168.1.0/24" 或 "192.168.1.1-192.168.1.254"
- `parse_port_range(port_str)` → 解析 "1-1024" 或 "80,443,8080"
- `get_service_name(port)` → 常见端口→服务名映射
- `export_json(results, filepath)` → JSON 导出
- `export_csv(results, filepath)` → CSV 导出

### `cli.py`
- argparse 子命令：`scan`（端口扫描）、`discover`（主机发现）
- 参数：`--host`, `--ports`, `--threads`, `--output`, `--format`

### `gui.py`
- tkinter 主窗口：
  - 输入区：目标 IP、端口范围、线程数
  - 进度条
  - 结果表格（主机 | 端口 | 状态 | 服务）
  - 导出按钮

## 数据流
```
用户输入(CLI/GUI) → ScanConfig → TCPScanner/ICMPScanner → [ScanResult] → 格式化 → 输出(屏幕/文件)
```
