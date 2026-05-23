import platform
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from scanner.engine import HostResult, HostStatus


class ICMPScanner:
    def __init__(self, timeout: float = 1.0, max_workers: int = 50) -> None:
        self.timeout = timeout
        self.max_workers = max_workers

    def ping(self, host: str) -> HostResult:
        start = time.perf_counter()

        if platform.system() == "Windows":
            timeout_ms = str(int(self.timeout * 1000))
            cmd = ["ping", "-n", "1", "-w", timeout_ms, host]
        else:
            timeout_sec = str(int(self.timeout))
            cmd = ["ping", "-c", "1", "-W", timeout_sec, host]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 1.0,
            )
            elapsed = time.perf_counter() - start

            if result.returncode == 0:
                return HostResult(
                    host=host, status=HostStatus.UP,
                    scan_time=round(elapsed, 4),
                )
            else:
                return HostResult(
                    host=host, status=HostStatus.DOWN,
                    scan_time=round(elapsed, 4),
                )
        except subprocess.TimeoutExpired:
            return HostResult(
                host=host, status=HostStatus.DOWN,
                scan_time=self.timeout,
            )
        except FileNotFoundError:
            return HostResult(
                host=host, status=HostStatus.UNKNOWN,
                error_message="ping command not found",
            )

    def discover_hosts(
        self,
        target_ips: list[str],
        on_result: Optional[Callable[[HostResult], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> list[HostResult]:
        results: list[HostResult] = []
        total = len(target_ips)

        max_workers = min(self.max_workers, total, 100)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.ping, ip): ip for ip in target_ips
            }
            completed = 0
            for future in as_completed(future_map):
                result = future.result()
                results.append(result)
                completed += 1
                if on_result:
                    on_result(result)
                if on_progress:
                    on_progress(completed, total)

        return results
