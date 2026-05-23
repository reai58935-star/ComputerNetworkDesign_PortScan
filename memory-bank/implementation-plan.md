# 实现计划

## 分步实现（每步一个可测试的 commit）

### 阶段一：项目骨架
- [ ] 1. 创建项目目录结构
- [ ] 2. 创建 `memory-bank/` 文档
- [ ] 3. 运行 `/init` 生成 `CLAUDE.md`

### 阶段二：核心扫描引擎
- [ ] 4. `scanner/utils.py` — IP/端口解析 + 服务名映射
- [ ] 5. `scanner/engine.py` — 数据类（ScanResult, HostResult, ScanConfig）
- [ ] 6. `scanner/tcp_scanner.py` — TCP connect 单端口 + 多线程扫描
- [ ] 7. `scanner/icmp_scanner.py` — ICMP echo 主机发现
- [ ] 8. 单元测试（test_utils.py, test_scanner.py）

### 阶段三：CLI 界面
- [ ] 9. `cli.py` — argparse 命令行接口

### 阶段四：GUI 界面
- [ ] 10. `gui.py` — tkinter 图形界面

### 阶段五：收尾
- [ ] 11. README.md 使用说明
- [ ] 12. 撰写课程设计报告
