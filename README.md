# Port Scanner — 端口扫描器

课程设计"设计题目四：端口扫描"。跨平台 TCP 端口扫描 + ICMP 主机发现工具，纯 Python 标准库，零外部依赖。

## 功能

- **TCP connect 端口扫描** — 多线程并发，支持单IP/CIDR/范围/域名
- **ICMP echo 主机发现** — 自动适配 Windows/Linux ping 参数
- **双界面** — CLI (argparse) + GUI (tkinter)
- **多种导出格式** — JSON / CSV / HTML / Markdown 报告

## 快速开始

```bash
# 扫描本地常用端口
python cli.py scan --target 127.0.0.1 --ports 1-1024

# 扫描网段 + 导出 HTML 报告
python cli.py scan --target 192.168.1.0/24 --ports 22,80,443,3306 --output report.html --format html

# 主机发现（ICMP ping）
python cli.py discover --network 192.168.1.0/24

# 启动图形界面
python gui.py
```

## CLI 命令

### scan — TCP 端口扫描

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--target`, `-t` | 目标 IP/CIDR/范围（必填） | — |
| `--ports`, `-p` | 端口范围 | `1-1024` |
| `--threads` | 最大并发线程数 | `100` |
| `--timeout` | 单连接超时（秒） | `1.0` |
| `--output`, `-o` | 输出文件路径 | — |
| `--format`, `-f` | 输出格式: json/csv/html/md | `html` |

### discover — ICMP 主机发现

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--network`, `-n` | 网络 CIDR/范围（必填） | — |
| `--threads` | 最大并发 ping 数 | `50` |
| `--timeout` | ping 超时（秒） | `1.0` |
| `--output`, `-o` | 输出文件路径 | — |
| `--format`, `-f` | 输出格式 | `html` |

## 运行测试

```bash
python -m unittest discover tests/ -v
```

## 项目结构

```
├── scanner/              # 核心扫描引擎（不依赖 UI）
│   ├── engine.py         # 数据类：ScanResult, HostResult, ScanConfig
│   ├── tcp_scanner.py    # TCP connect 扫描
│   ├── icmp_scanner.py   # ICMP host discovery
│   ├── utils.py          # IP/端口解析、服务名、导出
│   └── reporter.py       # HTML/Markdown 报告生成
├── cli.py                # 命令行界面
├── gui.py                # 图形界面
├── tests/                # 单元测试
└── memory-bank/          # 项目文档
```

## 依赖

Python 3.9+，无需安装任何第三方包。

## 注意事项

- 仅扫描你有权限的目标
- 大端口范围（1-65535）扫描可能耗时较长
- ICMP 扫描在某些网络环境下可能被防火墙阻止
