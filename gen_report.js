const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak, LevelFormat,
  TableOfContents
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, font: "SimHei", size: 22 })] })],
  });
}

function cell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "SimSun", size: 21 })] })],
  });
}

function codeCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Consolas", size: 18 })] })],
  });
}

function p(text, opts = {}) {
  const runs = [];
  if (typeof text === "string") {
    runs.push(new TextRun({ text, font: "SimSun", size: 21, ...opts }));
  } else {
    text.forEach(t => runs.push(new TextRun(t)));
  }
  return new Paragraph({
    spacing: { after: 120, before: 0 },
    children: runs,
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [new TextRun({ text, font: "SimSun", size: 21 })],
  });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { after: 180, before: 360 },
    children: [new TextRun({ text, font: "SimHei", size: 32, bold: true })],
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { after: 180, before: 240 },
    children: [new TextRun({ text, font: "SimHei", size: 28, bold: true })],
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "SimSun", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "SimHei" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "SimHei" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [
    // ===== TITLE PAGE =====
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "计算机网络课程设计", font: "SimHei", size: 18, color: "999999" })],
        })] }),
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun("第 "), new TextRun({ children: [PageNumber.CURRENT], font: "SimSun", size: 18 }), new TextRun(" 页")],
        })] }),
      },
      children: [
        new Paragraph({ spacing: { after: 2400 }, children: [] }),
        new Paragraph({ spacing: { after: 600 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "课程设计报告", font: "SimHei", size: 44, bold: true }),
        ] }),
        new Paragraph({ spacing: { after: 600 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "设计题目四：端口扫描", font: "SimHei", size: 32 }),
        ] }),
        new Paragraph({ spacing: { after: 1200 }, children: [] }),
        new Paragraph({ spacing: { after: 1200 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "基于 Python 的跨平台 TCP 端口扫描与 ICMP 主机发现工具", size: 24 }),
        ] }),
        new Paragraph({ spacing: { after: 300 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "含双界面（CLI + GUI）与自动报告生成", size: 24 }),
        ] }),
        new Paragraph({ spacing: { after: 1200 }, children: [] }),
        new Paragraph({ spacing: { after: 300 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "学院：__________  班级：__________", size: 24 }),
        ] }),
        new Paragraph({ spacing: { after: 300 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "姓名：__________  学号：__________", size: 24 }),
        ] }),
        new Paragraph({ spacing: { after: 600 }, alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "2026 年 5 月", size: 24 }),
        ] }),
      ],
    },

    // ===== MAIN CONTENT =====
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "计算机网络课程设计 — 端口扫描", font: "SimHei", size: 18, color: "999999" })],
        })] }),
      },
      footers: {
        default: new Footer({ children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun("第 "), new TextRun({ children: [PageNumber.CURRENT], font: "SimSun", size: 18 }), new TextRun(" 页")],
        })] }),
      },
      children: [
        // ====== TABLE OF CONTENTS ======
        new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({ children: [new PageBreak()] }),

        // ====== CHAPTER 1 ======
        heading1("一、系统需求"),

        heading2("1.1 设计目的"),
        bullet("通过文献检索掌握端口扫描的工作原理、工作流程，设计实现方案，并对方案做合理性论证。"),
        bullet("选择合适的开发工具、测试方法，设计实现扫描器。"),
        bullet("整理设计过程中的文档、代码，将设计、测试过程撰写成课程设计报告。"),

        heading2("1.2 功能需求"),
        p("本端口扫描器需实现以下核心功能："),
        bullet("网段扫描：支持输入 IP 范围（单IP、CIDR网段、IP范围、域名），自动解析并扫描。"),
        bullet("端口扫描：使用 TCP connect 方式，扫描指定主机的端口范围（1-65535），判断端口开放状态。"),
        bullet("主机发现：使用 ICMP echo 扫描（subprocess ping），检测局域网内存活主机。"),
        bullet("服务识别：内置 1023 个知名端口（1-1023 全覆盖）+ 约 180 个注册/高端口到服务名称的映射表，自动识别端口对应服务。"),
        bullet("结果展示：GUI 表格只显示开放端口，closed/filtered 后台保存用于导出。"),
        bullet("结果导出：支持 JSON、CSV、HTML、Markdown 四种格式。"),
        bullet("双界面：CLI 命令行（argparse 子命令）和 GUI 图形界面（黑客风暗色主题）。"),
        bullet("报告自动生成：扫描完成后自动生成 HTML/Markdown 格式的专业扫描报告。"),

        heading2("1.3 非功能性需求"),
        bullet("跨平台：Windows 和 Linux 均可运行，使用纯 Python 标准库。"),
        bullet("零外部依赖：仅使用 Python 3.9+ 标准库，无需 pip install 任何包。"),
        bullet("模块化：扫描引擎（scanner/）与 UI 层（cli.py / gui.py）严格分离，单向依赖。"),
        bullet("多线程并发：使用 ThreadPoolExecutor，默认 100 线程，可自定义。"),
        bullet("不要求管理员权限：TCP 扫描用 connect_ex()，ICMP 用 subprocess ping，均无需 root/admin。"),
        bullet("3 连续错误提前中止：避免在不可达主机上浪费时间。"),
        bullet("GUI 无阻塞：扫描在后台 daemon 线程运行，root.after() 跨线程更新 UI。"),

        // ====== CHAPTER 2 ======
        heading1("二、概要设计"),

        heading2("2.1 技术栈选择"),
        p("本项目选择 Python 3.9+ 作为开发语言。技术选型如下："),
        p([
          { text: "Python 标准库", font: "Consolas", size: 21, bold: true },
          { text: "：socket（TCP连接）、ipaddress（IP网段计算）、subprocess（ICMP ping）、threading / concurrent.futures（多线程并发）、tkinter（图形界面）、argparse（命令行解析）、json / csv（数据导出）、html（HTML 报告生成）。", font: "SimSun", size: 21 },
        ]),
        p("所有依赖均为 Python 标准库，零外部依赖，确保在任何安装 Python 3.9+ 的环境下直接运行。"),

        heading2("2.2 系统架构"),
        p("系统采用三层架构，严格单向依赖 —— 引擎层绝不引用 UI 层的任何模块。"),
        new Paragraph({ spacing: { after: 80 }, children: [] }),

        // Architecture diagram as code block
        ...[
          "  CLI (cli.py) / GUI (gui.py)    ← 展示层，不得被 scanner/ 引用",
          "         │",
          "  Scanner Engine（scanner/）      ← 业务逻辑，不 print()，无 UI 耦合",
          "    ├── engine.py      数据类（ScanResult, HostResult, ScanConfig）",
          "    ├── tcp_scanner.py  TCP connect 扫描 + ThreadPoolExecutor",
          "    ├── icmp_scanner.py ICMP echo 主机发现（subprocess ping）",
          "    ├── utils.py       IP/端口解析，1023 知名端口全覆盖，JSON/CSV 导出",
          "    └── reporter.py    HTML/Markdown 报告生成器",
          "         │",
          "  Python stdlib（socket, threading, tkinter） ← 零外部依赖",
        ].map(line => new Paragraph({
          spacing: { after: 40 },
          indent: { left: 360 },
          children: [new TextRun({ text: line, font: "Consolas", size: 18 })],
        })),

        new Paragraph({ spacing: { after: 120 }, children: [] }),

        heading2("2.3 模块职责表"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [1800, 2200, 5360],
          rows: [
            new TableRow({ children: [headerCell("模块", 1800), headerCell("文件", 2200), headerCell("职责说明", 5360)] }),
            new TableRow({ children: [cell("核心引擎", 1800), codeCell("engine.py", 2200), cell("PortStatus/HostStatus 枚举，ScanResult/HostResult/ScanConfig 数据类", 5360)] }),
            new TableRow({ children: [cell("TCP 扫描器", 1800), codeCell("tcp_scanner.py", 2200), cell("TCPScanner 类：connect_ex() 端口扫描，ThreadPoolExecutor 并发，3 连续错误提前中止", 5360)] }),
            new TableRow({ children: [cell("ICMP 扫描器", 1800), codeCell("icmp_scanner.py", 2200), cell("ICMPScanner 类：subprocess ping，自动适配 Win/Linux 参数", 5360)] }),
            new TableRow({ children: [cell("工具模块", 1800), codeCell("utils.py", 2200), cell("parse_ip_target/parse_port_range 解析，1023 知名端口全覆盖，export_json/export_csv 导出", 5360)] }),
            new TableRow({ children: [cell("报告生成", 1800), codeCell("reporter.py", 2200), cell("ReportGenerator 类：generate_html（内联 CSS）/ generate_markdown", 5360)] }),
            new TableRow({ children: [cell("命令行界面", 1800), codeCell("cli.py", 2200), cell("argparse 子命令 scan/discover，参数 --target --ports --threads --timeout --output --format", 5360)] }),
            new TableRow({ children: [cell("图形界面", 1800), codeCell("gui.py", 2200), cell("tkinter 黑客风暗色主题，后台 daemon 线程，root.after() 更新，只显示开放端口", 5360)] }),
            new TableRow({ children: [cell("GUI 启动器", 1800), codeCell("gui.pyw", 2200), cell("双击启动，无命令行窗口，唯一启动方式", 5360)] }),
            new TableRow({ children: [cell("测试", 1800), codeCell("tests/", 2200), cell("test_utils.py（17 测试）+ test_scanner.py（8 测试），共 25 个单元测试", 5360)] }),
          ],
        }),

        heading2("2.4 数据流"),
        p("用户输入 (CLI/GUI) → ScanConfig (targets, ports, timeout, max_workers) → TCPScanner / ICMPScanner → on_result 回调 → UI 实时更新表格 → 完成后 ReportGenerator → 导出 HTML/MD/JSON/CSV。"),
        new Paragraph({ spacing: { after: 80 }, children: [] }),

        // ====== CHAPTER 3 ======
        heading1("三、详细设计"),

        heading2("3.1 端口状态模型"),
        p("扫描引擎定义了四个端口状态枚举："),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2000, 1800, 5560],
          rows: [
            new TableRow({ children: [headerCell("枚举值", 2000), headerCell("含义", 1800), headerCell("判定条件", 5560)] }),
            new TableRow({ children: [codeCell("PortStatus.OPEN", 2000), cell("端口开放", 1800), cell("connect_ex() 返回 0", 5560)] }),
            new TableRow({ children: [codeCell("PortStatus.CLOSED", 2000), cell("端口关闭", 1800), cell("connect_ex() 返回非零（ECONNREFUSED 等）", 5560)] }),
            new TableRow({ children: [codeCell("PortStatus.FILTERED", 2000), cell("被过滤", 1800), cell("socket.timeout 超时", 5560)] }),
            new TableRow({ children: [codeCell("PortStatus.ERROR", 2000), cell("扫描错误", 1800), cell("DNS 解析失败 / OS 错误 / 主机不可达中止", 5560)] }),
          ],
        }),

        heading2("3.2 TCP 扫描流程"),
        p("TCPScanner 类包含三个层级的方法："),
        p([
          { text: "scan_port(host, port)", font: "Consolas", size: 21, bold: true },
          { text: " — 使用 socket.connect_ex() 连接单个端口。connect_ex() 返回错误码而非抛出异常，可以精确区分端口状态。创建 socket → settimeout → connect_ex() → close() 确保资源释放。", font: "SimSun", size: 21 },
        ]),
        p([
          { text: "scan_host(host, on_result)", font: "Consolas", size: 21, bold: true },
          { text: " — 使用 ThreadPoolExecutor 并发扫描该主机的所有端口。max_workers 取配置值、端口数和 500 的最小值。连续遇到 3 个 ERROR 或 FILTERED 状态时提前中止，剩余端口标记为 ERROR（\"host unreachable\"）。每完成一个端口通过 on_result 回调通知 UI。", font: "SimSun", size: 21 },
        ]),
        p([
          { text: "scan_network(on_result, on_progress)", font: "Consolas", size: 21, bold: true },
          { text: " — 串行遍历 target 列表中的每台主机，逐台调用 scan_host()。每台主机完成后通过 on_progress 回调通知进度。", font: "SimSun", size: 21 },
        ]),

        heading2("3.3 ICMP 主机发现"),
        p([
          { text: "ICMPScanner", font: "Consolas", size: 21, bold: true },
          { text: " 使用 subprocess 调用系统 ping 命令，避免 raw socket 需要管理员权限的问题。", font: "SimSun", size: 21 },
        ]),
        bullet("Windows：ping -n 1 -w <ms> <host>"),
        bullet("Linux：ping -c 1 -W <sec> <host>"),
        bullet("仅判断 returncode（0=可达，非0=不可达），不做输出解析。"),
        bullet("discover_hosts() 使用 ThreadPoolExecutor 并发 ping 多台主机。"),

        heading2("3.4 IP 与端口解析"),
        p("parse_ip_target(str) 支持四种输入格式："),
        bullet("单 IP：\"192.168.1.1\" → [\"192.168.1.1\"]"),
        bullet("CIDR 网段：\"192.168.1.0/30\" → [\"192.168.1.1\", \"192.168.1.2\"]"),
        bullet("IP 范围：\"10.0.0.1-10.0.0.3\" → [\"10.0.0.1\", \"10.0.0.2\", \"10.0.0.3\"]"),
        bullet("域名：\"localhost\" → [\"localhost\"]"),

        p("parse_port_range(str) 支持四种格式组合："),
        bullet("单端口：\"80\" → [80]"),
        bullet("端口范围：\"80-83\" → [80, 81, 82, 83]"),
        bullet("逗号分隔列表：\"22,80,443\" → [22, 80, 443]"),
        bullet("混合格式：\"22,80-82,443\" → [22, 80, 81, 82, 443]"),

        heading2("3.5 服务名称识别"),
        p("SERVICE_NAMES 字典内置 1023 个知名端口号（1-1023 全覆盖）到服务名称的映射，覆盖："),
        bullet("知名系统端口（0-1023）：HTTP(80)、HTTPS(443)、SSH(22)、FTP(21)、SMTP(25)、DNS(53)、TELNET(23) 等 100+ 个。"),
        bullet("注册端口（1024-49151）：MySQL(3306)、PostgreSQL(5432)、Redis(6379)、MongoDB(27017)、RDP(3389)、Docker(2375/2376) 等 150+ 个。"),
        bullet("常见高端口：Splunk(9997)、Webmin(10000)、Memcached(11211)、Minecraft(25565) 等 50+ 个。"),
        p("get_service_name(port) 通过字典查找返回服务名，未知端口返回 \"unknown\"。"),

        heading2("3.6 GUI 界面设计"),
        p("GUI 采用黑客风暗色主题设计，配色方案："),
        bullet("背景色 BG = #0a0a0a（纯黑），表面色 SURFACE = #0f0f0f（暗灰黑）"),
        bullet("主色调 GREEN = #00ff41（荧光绿），高亮 GREEN_HIGHLIGHT = #39ff14"),
        bullet("辅助色 CYAN = #00ffff，警告色 YELLOW = #ffcc00，错误 RED = #ff3333"),
        p("界面布局："),
        bullet("顶部 ASCII Art 字符画 Banner（╔══ PORT SCANNER ══╗ 框体）"),
        bullet("输入区：终端风格输入框，prompt 前缀（Target > / Ports > / Threads > / Timeout >）"),
        bullet("按钮：[ SCAN ]（绿色） / [ DISCOVER ]（青色） / [ STOP ]（红色） / [ EXPORT ]（灰色）"),
        bullet("输出区：Treeview 表格，HOST / PORT / STATUS / SERVICE 四列全部居中对齐"),
        bullet("状态标签：open = 荧光绿粗体，up = 青色，filtered = 黄色，error = 红色"),
        bullet("底部进度条 + 状态行（[ READY ] / [ SCANNING ] / [ DONE ]）"),
        p("GUI 扫描在后台 daemon 线程执行，通过 root.after() 跨线程安全更新 UI。扫描结果只显示开放端口（关闭/过滤端口后台保存用于导出）。"),
        p("启动方式：双击 gui.pyw（Windows 关联 pythonw.exe，无命令行窗口），唯一启动方式。"),

        heading2("3.7 报告生成"),
        p("ReportGenerator 类生成两种格式报告："),
        bullet("generate_html(path)：独立 HTML 文件，内联 CSS，包含总体摘要表、逐主机详表。绿色主题配色，栅格线区分。"),
        bullet("generate_markdown(path)：Markdown 格式，标题层级 + 表格，适合 Git 仓库文档。"),
        p("报告内容：扫描配置（目标、端口数、线程数、超时）→ 总体统计（主机数、开放端口数）→ 每主机开放端口列表。"),

        heading2("3.8 CLI 命令行接口"),
        p("cli.py 使用 argparse 提供两个子命令："),
        p([
          { text: "scan 子命令", font: "Consolas", size: 21, bold: true },
        ]),
        bullet("--target：目标 IP（支持单IP/CIDR/范围/域名），必填"),
        bullet("--ports：端口范围（如 1-1024 或 22,80,443），默认 1-1024"),
        bullet("--threads：最大并发线程数，默认 100"),
        bullet("--timeout：连接超时（秒），默认 1.0"),
        bullet("--output：输出文件路径"),
        bullet("--format：输出格式（json/csv/html/md），默认 html"),

        p([
          { text: "discover 子命令", font: "Consolas", size: 21, bold: true },
        ]),
        bullet("--network：目标网段（支持单IP/CIDR/范围/域名），必填"),
        bullet("--threads：最大并发线程数，默认 50"),
        bullet("--timeout：ping 超时（秒），默认 1.0"),
        bullet("--output / --format：同 scan 子命令"),

        // ====== CHAPTER 4 ======
        heading1("四、测试"),

        heading2("4.1 测试策略"),
        p("采用 unittest 框架，两个测试文件共 25 个测试用例，覆盖以下方面："),
        bullet("IP 解析：单 IP / CIDR / IP 范围 / 域名 / 空输入 / 非法输入 / 反向范围"),
        bullet("端口解析：单端口 / 范围 / 逗号分隔 / 混合 / 越界 / 空输入 / 非法字符"),
        bullet("服务名查询：已知端口 (80→http, 443→https, 22→ssh) / 未知端口 (65000→unknown)"),
        bullet("TCP 扫描：localhost 开放端口 / 关闭端口 / 批量扫描 / 配置默认值 / 自定义配置"),
        bullet("ICMP 发现：localhost ping / 无效主机 ping / 网段批量发现"),

        heading2("4.2 测试结果"),
        new Paragraph({ spacing: { after: 60 }, children: [] }),
        new Paragraph({
          spacing: { after: 40 },
          indent: { left: 360 },
          children: [new TextRun({ text: "Ran 25 tests in 1.669s", font: "Consolas", size: 18, bold: true })],
        }),
        new Paragraph({
          spacing: { after: 40 },
          indent: { left: 360 },
          children: [new TextRun({ text: "OK", font: "Consolas", size: 18, bold: true, color: "00AA00" })],
        }),
        new Paragraph({ spacing: { after: 120 }, children: [] }),
        p("所有 25 个测试用例全部通过，无失败，无错误。"),

        heading2("4.3 功能验证"),
        p("除单元测试外，还进行了以下手动功能验证："),
        bullet("CLI 扫描本地：python cli.py scan --target 127.0.0.1 --ports 1-1024 → 发现 135 端口开放 (msrpc 服务)"),
        bullet("CLI 发现主机：python cli.py discover --target 127.0.0.1 → 检测到存活主机 1 台"),
        bullet("GUI 操作：启动 gui.pyw → 输入目标 → 点击 SCAN → 表格实时显示开放端口 → EXPORT 导出报告"),
        bullet("HTML 报告：浏览器打开，格式正确，包含 summary 和 per-host 表格"),

        // ====== CHAPTER 5 ======
        heading1("五、程序详细设计说明"),

        heading2("5.1 项目结构"),
        new Paragraph({ spacing: { after: 80 }, children: [] }),
        ...[
          "ComputerNetworkDesign/",
          "├── scanner/",
          "│   ├── __init__.py       包初始化 + 公共接口导出",
          "│   ├── engine.py         数据模型（枚举 + 数据类）",
          "│   ├── tcp_scanner.py    TCP 端口扫描器",
          "│   ├── icmp_scanner.py   ICMP 主机发现器",
          "│   ├── utils.py          工具函数 + 1023 知名端口全覆盖",
          "│   └── reporter.py       HTML/MD 报告生成器",
          "├── tests/",
          "│   ├── test_utils.py     17 个单元测试",
          "│   └── test_scanner.py   8 个单元测试",
          "├── cli.py               命令行界面（argparse）",
          "├── gui.py               GUI 主程序（tkinter）",
          "├── gui.pyw              双击启动器（无命令行）",
          "├── CLAUDE.md            项目文档",
          "└── 课程设计报告.docx     本报告",
        ].map(line => new Paragraph({
          spacing: { after: 30 },
          indent: { left: 360 },
          children: [new TextRun({ text: line, font: "Consolas", size: 18 })],
        })),

        heading2("5.2 关键数据结构"),
        p([
          { text: "ScanResult", font: "Consolas", size: 21, bold: true },
          { text: "（dataclass）：host: str, port: int, status: PortStatus, service: str = \"unknown\", error_message: str = \"\"", font: "Consolas", size: 20 },
        ]),
        p([
          { text: "HostResult", font: "Consolas", size: 21, bold: true },
          { text: "（dataclass）：host: str, status: HostStatus, open_ports: list[ScanResult], scan_time: float, error_message: str", font: "Consolas", size: 20 },
        ]),
        p([
          { text: "ScanConfig", font: "Consolas", size: 21, bold: true },
          { text: "（dataclass）：targets: list[str], ports: list[int], timeout: float = 1.0, max_workers: int = 100", font: "Consolas", size: 20 },
        ]),

        heading2("5.3 双回调模式"),
        p("扫描器采用回调模式向 UI 层报告进度，保持引擎与 UI 的完全解耦："),
        bullet("on_result(ScanResult)：每完成一个端口扫描时调用，CLI 端 print 输出，GUI 端通过 root.after() 跨线程插入表格行。"),
        bullet("on_progress(done: int, total: int)：每完成一台主机扫描时调用，用于更新进度条。"),
        bullet("GUI 端在 _on_scan_result 中只将 open 状态的结果插入 Treeview，filtered/closed/error 结果仅保存到 _results 列表供导出使用。"),

        heading2("5.4 线程安全设计"),
        bullet("扫描在后台 daemon 线程 (threading.Thread) 中执行，不阻塞 GUI 主线程。"),
        bullet("所有 UI 更新通过 root.after(0, callback, ...) 调度到主线程执行。"),
        bullet("daemon=True 确保窗口关闭后后台线程自动终止。"),
        bullet("ThreadPoolExecutor 的 max_workers 通过 ScanConfig 控制，取 min(用户设置, 端口数, 500)。"),

        // ====== CHAPTER 6 ======
        heading1("六、收获与总结"),

        heading2("6.1 技术收获"),
        bullet("深入理解了 TCP 三次握手与端口扫描原理。connect_ex() 返回值（0/非0）而非抛异常，精确区分端口状态。"),
        bullet("掌握了 Python socket 编程，包括超时控制、资源释放（try/finally sock.close()）、错误处理。"),
        bullet("掌握了 ThreadPoolExecutor 并发模式，避免手动管理线程和队列。"),
        bullet("掌握了 tkinter 图形界面开发，特别是后台线程 + root.after() 的跨线程安全更新模式。"),
        bullet("理解了 IP 地址的 CIDR 表示法和网段计算方法（ipaddress 模块）。"),
        bullet("学会了使用 subprocess 调用系统命令实现跨平台的 ICMP ping。"),

        heading2("6.2 设计心得"),
        bullet("模块分层设计带来的好处：scanner/ 引擎层完全不依赖 UI，使得 CLI 和 GUI 可以共享同一套扫描逻辑，修改引擎不影响界面。"),
        bullet("双回调模式 (on_result + on_progress) 是一个简单但有效的解耦方案，避免引擎层直接操作 UI。"),
        bullet("1023 端口全覆盖的服务映射表大大提升了扫描结果的可读性，用户一眼就能知道开放端口对应的服务。"),
        bullet("黑客风 GUI 的暗色主题不仅美观，还降低了长时间使用时的视觉疲劳。"),
        bullet("3 连续错误提前中止机制在实际测试中显著减少了在不可达主机上的等待时间。"),
        bullet("零外部依赖的设计使得项目在任何安装了 Python 3.9+ 的环境中可以直接运行，极大降低了部署成本。"),

        heading2("6.3 不足与改进方向"),
        bullet("当前仅支持 TCP connect 扫描，后续可扩展 SYN 半开扫描和 UDP 扫描。"),
        bullet("ICMP 主机发现依赖系统 ping 命令，速度受限于系统实现，可考虑异步 I/O。"),
        bullet("GUI 界面可进一步优化，如增加端口筛选、搜索、扫描历史记录功能。"),
        bullet("目前不支持 IPv6，可通过兼容 socket.AF_INET6 扩展。"),
      ],
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("E:\\class\\ComputerNetworkDesign\\课程设计报告.docx", buffer);
  console.log("Report generated successfully.");
});
