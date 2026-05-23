import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from scanner import (
    TCPScanner, ICMPScanner, ScanConfig,
    parse_ip_target, parse_port_range,
    export_json, export_csv, ReportGenerator,
)


class PortScannerGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Port Scanner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self._scanning = False
        self._results: list = []
        self._config: ScanConfig | None = None

        self._build_input_area()
        self._build_result_area()
        self._build_status_bar()

    def _build_input_area(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Scan Configuration", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Row 0: target
        ttk.Label(frame, text="Target:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.target_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(frame, textvariable=self.target_var, width=40).grid(row=0, column=1, sticky=tk.W)

        # Row 1: ports
        ttk.Label(frame, text="Ports:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.ports_var = tk.StringVar(value="1-1024")
        ttk.Entry(frame, textvariable=self.ports_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # Row 2: threads + timeout
        ttk.Label(frame, text="Threads:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.threads_var = tk.IntVar(value=100)
        ttk.Spinbox(frame, from_=1, to=500, textvariable=self.threads_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        ttk.Label(frame, text="Timeout (s):").grid(row=2, column=1, sticky=tk.E, padx=(0, 5))
        self.timeout_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(frame, from_=0.1, to=10.0, increment=0.5, textvariable=self.timeout_var, width=8).grid(row=2, column=2, sticky=tk.W, padx=(5, 0))

        # Row 3: buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        self.scan_btn = ttk.Button(btn_frame, text="Port Scan", command=self._start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.discover_btn = ttk.Button(btn_frame, text="Host Discovery", command=self._start_discover)
        self.discover_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.export_btn = ttk.Button(btn_frame, text="Export...", command=self._export)
        self.export_btn.pack(side=tk.LEFT)

    def _build_result_area(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("host", "port", "status", "service")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        self.tree.heading("host", text="Host")
        self.tree.heading("port", text="Port")
        self.tree.heading("status", text="Status")
        self.tree.heading("service", text="Service")
        self.tree.column("host", width=150)
        self.tree.column("port", width=80)
        self.tree.column("status", width=80)
        self.tree.column("service", width=120)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_status_bar(self) -> None:
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=5)

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.status_var).pack(side=tk.RIGHT)

    def _start_scan(self) -> None:
        try:
            targets = parse_ip_target(self.target_var.get())
            ports = parse_port_range(self.ports_var.get())
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        self._config = ScanConfig(
            targets=targets, ports=ports,
            timeout=self.timeout_var.get(), max_workers=self.threads_var.get(),
        )
        self._results = []
        self._clear_tree()
        self._set_scanning(True)
        self.status_var.set(f"Scanning {len(targets)} host(s) x {len(ports)} port(s)...")

        scanner = TCPScanner(self._config)

        def run() -> None:
            scanner.scan_network(
                on_result=self._on_scan_result,
                on_progress=self._on_scan_progress,
            )
            self.root.after(0, self._scan_done)

        self._scan_thread = threading.Thread(target=run, daemon=True)
        self._scan_thread.start()

    def _start_discover(self) -> None:
        try:
            targets = parse_ip_target(self.target_var.get())
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        self._config = ScanConfig(targets=targets, ports=[])
        self._results = []
        self._clear_tree()
        self._set_scanning(True)
        self.status_var.set(f"Discovering {len(targets)} host(s)...")

        scanner = ICMPScanner(timeout=self.timeout_var.get(), max_workers=self.threads_var.get())

        def run() -> None:
            scanner.discover_hosts(
                targets,
                on_result=self._on_discover_result,
                on_progress=self._on_discover_progress,
            )
            self.root.after(0, self._scan_done)

        self._scan_thread = threading.Thread(target=run, daemon=True)
        self._scan_thread.start()

    def _on_scan_result(self, result) -> None:
        self.root.after(0, self._insert_result, result)

    def _on_discover_result(self, result) -> None:
        self._results.append(result)
        if result.status.value == "up":
            self.root.after(0, self._insert_row, result.host, "", "up", "")

    def _insert_result(self, result) -> None:
        if result.status.value in ("open", "up"):
            self._insert_row(result.host, str(result.port), result.status.value, result.service)

    def _insert_row(self, host: str, port: str, status: str, service: str) -> None:
        self.tree.insert("", tk.END, values=(host, port, status, service))

    def _on_scan_progress(self, done: int, total: int) -> None:
        self.root.after(0, self._update_progress, done, total)

    def _on_discover_progress(self, done: int, total: int) -> None:
        self.root.after(0, self._update_progress, done, total)

    def _update_progress(self, done: int, total: int) -> None:
        self.progress["maximum"] = total
        self.progress["value"] = done

    def _scan_done(self) -> None:
        self._set_scanning(False)
        total = sum(len(h.open_ports) for h in self._results) if self._results else 0
        hosts = len(self._results)
        self.status_var.set(f"Done. {hosts} host(s), {total} open port(s).")

    def _stop(self) -> None:
        self._set_scanning(False)
        self.status_var.set("Stopped.")

    def _export(self) -> None:
        if not self._config:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[
                ("HTML Report", "*.html"),
                ("Markdown Report", "*.md"),
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
            ],
        )
        if not filepath:
            return

        if filepath.endswith(".json"):
            export_json(self._results, filepath)
        elif filepath.endswith(".csv"):
            export_csv(self._results, filepath)
        elif filepath.endswith(".md"):
            ReportGenerator(self._results, self._config).generate_markdown(filepath)
        else:
            ReportGenerator(self._results, self._config).generate_html(filepath)
        self.status_var.set(f"Exported to {filepath}")

    def _set_scanning(self, scanning: bool) -> None:
        self._scanning = scanning
        state = tk.DISABLED if scanning else tk.NORMAL
        self.scan_btn.config(state=state)
        self.discover_btn.config(state=state)
        self.stop_btn.config(state=tk.NORMAL if scanning else tk.DISABLED)

    def _clear_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    PortScannerGUI().run()
