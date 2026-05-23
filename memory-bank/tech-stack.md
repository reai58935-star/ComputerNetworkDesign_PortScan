# 技术栈选择

## 编程语言
**Python 3.9+** — 内置 socket 库，跨平台，零外部依赖

## 核心依赖（全部标准库，无需 pip install）
| 模块 | 用途 |
|------|------|
| `socket` | TCP connect 扫描、原始套接字 |
| `argparse` | CLI 参数解析 |
| `tkinter` | GUI 图形界面 |
| `threading` | 多线程并发扫描 |
| `ipaddress` | IP 网段计算（如 192.168.1.0/24） |
| `json` | JSON 结果导出 |
| `csv` | CSV 结果导出 |
| `struct` | ICMP 报文构造 |
| `os` / `sys` | 系统判断、权限检测 |

## 开发工具
- IDE：VSCode / PyCharm（用户自选）
- 版本管理：Git
- 测试框架：unittest（Python 内置）

## 运行环境
- Windows 10/11 或 Linux（Ubuntu/Debian）
- Python 3.9 及以上
- 不需要管理员/root 权限
