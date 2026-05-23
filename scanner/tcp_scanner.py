import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from scanner.engine import ScanResult, HostResult, ScanConfig, PortStatus, HostStatus
from scanner.utils import get_service_name


class TCPScanner:
    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self._abort_host_threshold = 3

    def scan_port(self, host: str, port: int) -> ScanResult:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.config.timeout)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                return ScanResult(
                    host=host, port=port, status=PortStatus.OPEN,
                    service=get_service_name(port),
                )
            else:
                return ScanResult(
                    host=host, port=port, status=PortStatus.CLOSED,
                    service=get_service_name(port),
                )
        except socket.timeout:
            return ScanResult(
                host=host, port=port, status=PortStatus.FILTERED,
                service=get_service_name(port), error_message="timeout",
            )
        except socket.gaierror as e:
            return ScanResult(
                host=host, port=port, status=PortStatus.ERROR,
                error_message=f"DNS error: {e}",
            )
        except OSError as e:
            return ScanResult(
                host=host, port=port, status=PortStatus.ERROR,
                error_message=str(e),
            )
        finally:
            sock.close()

    def scan_host(
        self,
        host: str,
        on_result: Optional[Callable[[ScanResult], None]] = None,
    ) -> HostResult:
        host_start = time.perf_counter()
        consecutive_errors = 0
        results: list[ScanResult] = []
        scanned_ports: set[int] = set()

        max_workers = min(self.config.max_workers, len(self.config.ports), 500)
        if max_workers < 1:
            max_workers = 1

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.scan_port, host, port): port
                for port in self.config.ports
            }

            for future in as_completed(future_map):
                result = future.result()
                results.append(result)
                scanned_ports.add(result.port)

                if result.status in (PortStatus.ERROR, PortStatus.FILTERED):
                    consecutive_errors += 1
                    if consecutive_errors >= self._abort_host_threshold:
                        for f in future_map:
                            f.cancel()
                        break
                elif result.status == PortStatus.OPEN:
                    consecutive_errors = 0
                elif result.status == PortStatus.CLOSED:
                    consecutive_errors = 0

                if on_result:
                    on_result(result)

        # Mark unscanned ports as error (host unreachable abort)
        for port in self.config.ports:
            if port not in scanned_ports:
                r = ScanResult(
                    host=host, port=port, status=PortStatus.ERROR,
                    error_message="host unreachable, scan aborted",
                )
                results.append(r)
                if on_result:
                    on_result(r)

        elapsed = time.perf_counter() - host_start
        open_ports = [r for r in results if r.status == PortStatus.OPEN]
        host_status = HostStatus.UP if open_ports else HostStatus.DOWN

        return HostResult(
            host=host, status=host_status,
            open_ports=open_ports, scan_time=round(elapsed, 4),
        )

    def scan_network(
        self,
        on_result: Optional[Callable[[ScanResult], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> list[HostResult]:
        all_results: list[HostResult] = []
        total = len(self.config.targets)

        for i, host in enumerate(self.config.targets):
            host_result = self.scan_host(host, on_result=on_result)
            all_results.append(host_result)
            if on_progress:
                on_progress(i + 1, total)

        return all_results
