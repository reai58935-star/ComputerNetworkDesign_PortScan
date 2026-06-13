import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from scanner import (
    TCPScanner, ICMPScanner, ScanConfig,
    parse_ip_target, parse_port_range,
    export_json, export_csv, ReportGenerator,
)

# ---- colors ----
BG = "#0a0a0a"
SURFACE = "#0f0f0f"
GREEN = "#00ff41"
GREEN_DIM = "#00cc33"
GREEN_DARK = "#0d2818"
GREEN_HIGHLIGHT = "#39ff14"
WHITE = "#e0e0e0"
GRAY = "#555555"
GRAY_DIM = "#2a2a2a"
RED = "#ff3333"
YELLOW = "#ffcc00"
CYAN = "#00ffff"


def _ascii_art() -> str:
    return r"""
    ╔══════════════════════════════════════════╗
    ║       ██████╗  ██████╗ ██████╗ ████████╗  ║
    ║       ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝  ║
    ║       ██████╔╝██║   ██║██████╔╝   ██║     ║
    ║       ██╔═══╝ ██║   ██║██╔══██╗   ██║     ║
    ║       ██║     ╚██████╔╝██║  ██║   ██║     ║
    ║       ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝     ║
    ║                                            ║
    ║     ███████╗ ██████╗ █████╗ ███╗  ██╗      ║
    ║     ██╔════╝██╔════╝██╔══██╗████╗ ██║      ║
    ║     ███████╗██║     ███████║██╔██╗██║      ║
    ║     ╚════██║██║     ██╔══██║██║╚████║      ║
    ║     ███████║╚██████╗██║  ██║██║ ╚███║      ║
    ║     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚══╝      ║
    ╚══════════════════════════════════════════╝"""


class PortScannerGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("PORT SCANNER v2.0")
        self.root.geometry("900x720")
        self.root.configure(bg=BG)

        self._scanning = False
        self._results: list = []
        self._config: ScanConfig | None = None
        self._open_count = 0
        self._export_data: list = []  # HostResult list from scan_network/discover_hosts, for export

        self._build_styles()
        self._build_banner()
        self._build_input_section()
        self._build_output_section()
        self._build_status_line()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Hacker.TFrame", background=BG)
        style.configure("Surface.TFrame", background=SURFACE)

        style.configure("Hack.Treeview",
            background=SURFACE, foreground=GREEN,
            fieldbackground=SURFACE, borderwidth=0,
            font=("Consolas", 10), rowheight=26)
        style.configure("Hack.Treeview.Heading",
            background=GREEN_DARK, foreground=GREEN_HIGHLIGHT,
            font=("Consolas", 10, "bold"), borderwidth=0, padding=(8, 4))
        style.map("Hack.Treeview",
            background=[("selected", GREEN_DARK)],
            foreground=[("selected", GREEN_HIGHLIGHT)])

        style.configure("Hack.Horizontal.TProgressbar",
            troughcolor=SURFACE, background=GREEN_DIM, thickness=4,
            borderwidth=0, darkcolor=GREEN_DIM, lightcolor=GREEN_DIM)

    def _make_terminal_entry(self, parent, var, width, prompt_text) -> tk.Frame:
        """Entry styled like a terminal prompt: [>] hostname █"""
        frame = tk.Frame(parent, bg=SURFACE, highlightbackground=GRAY_DIM, highlightthickness=1)
        inner = tk.Frame(frame, bg=SURFACE)
        inner.pack(padx=10, pady=7, fill=tk.X)

        prompt = tk.Label(inner, text=f"{prompt_text} >", bg=SURFACE, fg=GREEN_HIGHLIGHT,
                          font=("Consolas", 11, "bold"))
        prompt.pack(side=tk.LEFT, padx=(0, 6))

        entry = tk.Entry(inner, textvariable=var, width=width,
                         font=("Consolas", 11), bg=SURFACE, fg=GREEN,
                         insertbackground=GREEN_HIGHLIGHT, bd=0,
                         relief=tk.FLAT, highlightthickness=0)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return frame

    def _make_btn(self, parent, text, color, cmd) -> tk.Button:
        colors = {
            "green": (GREEN_DARK, GREEN, "#003d00", GREEN_HIGHLIGHT),
            "cyan": ("#001a1a", CYAN, "#002222", "#88ffff"),
            "red": ("#1a0000", RED, "#330000", "#ff6666"),
            "dim": (GRAY_DIM, GRAY, "#1a1a1a", "#888888"),
        }
        bg_c, fg_c, active_bg, active_fg = colors.get(color, colors["dim"])

        return tk.Button(parent, text=text, command=cmd,
                         bg=bg_c, fg=fg_c, font=("Consolas", 11, "bold"),
                         activebackground=active_bg, activeforeground=active_fg,
                         relief=tk.FLAT, borderwidth=1,
                         padx=22, pady=8, cursor="hand2",
                         highlightbackground=GRAY_DIM, highlightthickness=1)

    def _build_banner(self) -> None:
        container = tk.Frame(self.root, bg=BG, height=200)
        container.pack(fill=tk.X, padx=12, pady=(12, 0))
        container.pack_propagate(False)

        # ASCII art banner
        banner_frame = tk.Frame(container, bg=GREEN_DARK, highlightbackground=GREEN, highlightthickness=1)
        banner_frame.pack(fill=tk.BOTH, expand=True)

        ascii_lines = _ascii_art().strip().split("\n")
        for line in ascii_lines:
            tk.Label(banner_frame, text=line, bg=GREEN_DARK, fg=GREEN_HIGHLIGHT,
                     font=("Consolas", 16)).pack()

    def _build_input_section(self) -> None:
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill=tk.X, padx=12, pady=(10, 0))

        # Decorative section label
        lbl_frame = tk.Frame(frame, bg=BG)
        lbl_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(lbl_frame, text="[*]", bg=BG, fg=GREEN_HIGHLIGHT,
                 font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(lbl_frame, text="TARGET CONFIGURATION",
                 bg=BG, fg=GREEN_DIM, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(lbl_frame, text="─" * 60, bg=BG, fg=GRAY_DIM,
                 font=("Consolas", 9)).pack(side=tk.LEFT, padx=(12, 0))

        row1 = tk.Frame(frame, bg=BG)
        row1.pack(fill=tk.X, pady=(0, 6))

        self.target_var = tk.StringVar(value="127.0.0.1")
        target_entry = self._make_terminal_entry(row1, self.target_var, 26, "Target")
        target_entry.pack(side=tk.LEFT, padx=(0, 8))

        self.ports_var = tk.StringVar(value="1-1024")
        ports_entry = self._make_terminal_entry(row1, self.ports_var, 18, "Ports")
        ports_entry.pack(side=tk.LEFT)

        row2 = tk.Frame(frame, bg=BG)
        row2.pack(fill=tk.X)

        self.threads_var = tk.IntVar(value=100)
        threads_entry = self._make_terminal_entry(row2, self.threads_var, 6, "Threads")
        threads_entry.pack(side=tk.LEFT, padx=(0, 8))

        self.timeout_var = tk.DoubleVar(value=1.0)
        timeout_entry = self._make_terminal_entry(row2, self.timeout_var, 6, "Timeout")
        timeout_entry.pack(side=tk.LEFT, padx=(0, 20))

        self.scan_btn = self._make_btn(row2, "[ SCAN ]", "green", self._start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.discover_btn = self._make_btn(row2, "[ DISCOVER ]", "cyan", self._start_discover)
        self.discover_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.stop_btn = self._make_btn(row2, "[ STOP ]", "red", self._stop)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.stop_btn.configure(state=tk.DISABLED, fg="#660000")

        self.export_btn = self._make_btn(row2, "[ EXPORT ]", "dim", self._export)
        self.export_btn.pack(side=tk.LEFT)

    def _build_output_section(self) -> None:
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Section label
        lbl_frame = tk.Frame(frame, bg=BG)
        lbl_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(lbl_frame, text="[+]", bg=BG, fg=GREEN_HIGHLIGHT,
                 font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(lbl_frame, text="SCAN OUTPUT",
                 bg=BG, fg=GREEN_DIM, font=("Consolas", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(lbl_frame, text="─" * 70, bg=BG, fg=GRAY_DIM,
                 font=("Consolas", 9)).pack(side=tk.LEFT, padx=(12, 0))

        self.stats_var = tk.StringVar(value="0 hosts  ·  0 open ports")
        tk.Label(lbl_frame, textvariable=self.stats_var, bg=BG, fg=CYAN,
                 font=("Consolas", 9)).pack(side=tk.RIGHT)

        # Terminal output - treeview with grid overlay
        table_frame = tk.Frame(frame, bg=SURFACE, highlightbackground=GRAY_DIM, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("host", "port", "status", "service")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 height=16, style="Hack.Treeview")
        self.tree.heading("host", text="HOST", anchor=tk.CENTER)
        self.tree.heading("port", text="PORT", anchor=tk.CENTER)
        self.tree.heading("status", text="STATUS", anchor=tk.CENTER)
        self.tree.heading("service", text="SERVICE", anchor=tk.CENTER)
        self.tree.column("host", width=200, minwidth=140, anchor=tk.CENTER)
        self.tree.column("port", width=70, minwidth=60, anchor=tk.CENTER)
        self.tree.column("status", width=80, minwidth=70, anchor=tk.CENTER)
        self.tree.column("service", width=150, minwidth=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # status tags
        self.tree.tag_configure("open", foreground=GREEN_HIGHLIGHT, font=("Consolas", 10, "bold"))
        self.tree.tag_configure("up", foreground=CYAN)
        self.tree.tag_configure("filtered", foreground=YELLOW)
        self.tree.tag_configure("error", foreground=RED)

    def _build_status_line(self) -> None:
        frame = tk.Frame(self.root, bg=SURFACE, height=32)
        frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        frame.pack_propagate(False)

        inner = tk.Frame(frame, bg=SURFACE)
        inner.pack(fill=tk.X, padx=12)

        self.progress = ttk.Progressbar(inner, mode="determinate",
                                        style="Hack.Horizontal.TProgressbar")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        self.status_var = tk.StringVar(value="[ READY ]  Awaiting command...")
        tk.Label(inner, textvariable=self.status_var, bg=SURFACE, fg=GREEN,
                 font=("Consolas", 9)).pack(side=tk.RIGHT)

    # ---- Scan logic ----

    def _start_scan(self) -> None:
        try:
            targets = parse_ip_target(self.target_var.get())
            ports = parse_port_range(self.ports_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        self._config = ScanConfig(targets=targets, ports=ports,
                                  timeout=self.timeout_var.get(),
                                  max_workers=self.threads_var.get())
        self._results = []
        self._open_count = 0
        self._clear_table()
        self._set_scanning(True)
        self.status_var.set(f"[ SCANNING ]  {len(targets)} host(s) x {len(ports)} port(s)...")

        scanner = TCPScanner(self._config)

        def run() -> None:
            host_results = scanner.scan_network(on_result=self._on_scan_result,
                                                on_progress=self._on_scan_progress)
            self.root.after(0, self._scan_done, host_results)

        self._scan_thread = threading.Thread(target=run, daemon=True)
        self._scan_thread.start()

    def _start_discover(self) -> None:
        try:
            targets = parse_ip_target(self.target_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        self._config = ScanConfig(targets=targets, ports=[])
        self._results = []
        self._open_count = 0
        self._clear_table()
        self._set_scanning(True)
        self.status_var.set(f"[ DISCOVERING ]  {len(targets)} host(s)...")

        scanner = ICMPScanner(timeout=self.timeout_var.get(),
                              max_workers=self.threads_var.get())

        def run() -> None:
            host_results = scanner.discover_hosts(targets,
                                                  on_result=self._on_discover_result,
                                                  on_progress=self._on_discover_progress)
            self.root.after(0, self._scan_done, host_results)

        self._scan_thread = threading.Thread(target=run, daemon=True)
        self._scan_thread.start()

    def _on_scan_result(self, result) -> None:
        self._results.append(result)
        if result.status.value in ("open", "up"):
            self._open_count += 1
            self.root.after(0, self._insert_row, result.host, str(result.port),
                            result.status.value, result.service)
        # Only show open ports in the table; closed/filtered are saved for export

    def _on_discover_result(self, result) -> None:
        self._results.append(result)
        if result.status.value == "up":
            self.root.after(0, self._insert_row, result.host, "", "up", "")

    def _insert_row(self, host: str, port: str, status: str, service: str) -> None:
        tag = status if status in ("open", "up", "filtered", "error") else ""
        self.tree.insert("", tk.END, values=(host, port, status, service),
                         tags=(tag,) if tag else ())

    def _on_scan_progress(self, done: int, total: int) -> None:
        self.root.after(0, self._update_progress, done, total)

    def _on_discover_progress(self, done: int, total: int) -> None:
        self.root.after(0, self._update_progress, done, total)

    def _update_progress(self, done: int, total: int) -> None:
        self.progress["maximum"] = total
        self.progress["value"] = done

    def _scan_done(self, host_results: list | None = None) -> None:
        self._set_scanning(False)
        if host_results is not None:
            self._export_data = host_results
        total = len(self._results)
        host_set: set[str] = {r.host for r in self._results}
        hosts = len(host_set)
        self.status_var.set(f"[ DONE ]  {hosts} host(s)  |  {total} scanned  |  {self._open_count} open")
        self.stats_var.set(f"{hosts} hosts  ·  {total} scanned  ·  {self._open_count} open")

    def _stop(self) -> None:
        self._set_scanning(False)
        self.status_var.set("[ STOPPED ]  Scan terminated by user")

    def _export(self) -> None:
        if not self._config or not self._export_data:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Report", "*.html"), ("Markdown Report", "*.md"),
                       ("JSON", "*.json"), ("CSV", "*.csv")])
        if not filepath:
            return
        if filepath.endswith(".json"):
            export_json(self._export_data, filepath)
        elif filepath.endswith(".csv"):
            export_csv(self._export_data, filepath)
        elif filepath.endswith(".md"):
            ReportGenerator(self._export_data, self._config).generate_markdown(filepath)
        else:
            ReportGenerator(self._export_data, self._config).generate_html(filepath)
        self.status_var.set(f"[ EXPORTED ]  {filepath}")

    def _set_scanning(self, scanning: bool) -> None:
        self._scanning = scanning
        state = tk.DISABLED if scanning else tk.NORMAL
        self.scan_btn.configure(state=state, fg=GREEN if not scanning else "#003d00")
        self.discover_btn.configure(state=state, fg=CYAN if not scanning else "#002222")
        self.stop_btn.configure(state=tk.NORMAL if scanning else tk.DISABLED,
                                fg=RED if scanning else "#660000")

    def _clear_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def run(self) -> None:
        self.root.mainloop()

    def destroy(self) -> None:
        self.root.destroy()
