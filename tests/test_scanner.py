import unittest
import socket
import threading
import time

from scanner.engine import ScanConfig, PortStatus, HostStatus
from scanner.tcp_scanner import TCPScanner
from scanner.icmp_scanner import ICMPScanner


class TestTCPScanner(unittest.TestCase):
    def test_scan_port_open(self) -> None:
        # Open a temporary server on a random port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        config = ScanConfig(targets=["127.0.0.1"], ports=[port], timeout=1.0, max_workers=1)
        scanner = TCPScanner(config)
        result = scanner.scan_port("127.0.0.1", port)

        self.assertEqual(result.status, PortStatus.OPEN)
        server.close()

    def test_scan_port_closed(self) -> None:
        # Find a port that is very likely closed
        config = ScanConfig(targets=["127.0.0.1"], ports=[59999], timeout=0.5, max_workers=1)
        scanner = TCPScanner(config)
        result = scanner.scan_port("127.0.0.1", 59999)

        self.assertIn(result.status, (PortStatus.CLOSED, PortStatus.FILTERED))

    def test_scan_host(self) -> None:
        config = ScanConfig(targets=["127.0.0.1"], ports=[22, 80], timeout=0.5, max_workers=2)
        scanner = TCPScanner(config)
        result = scanner.scan_host("127.0.0.1")

        self.assertIsInstance(result.host, str)
        self.assertIn(result.status, (HostStatus.UP, HostStatus.DOWN))


class TestICMPScanner(unittest.TestCase):
    def test_ping_localhost(self) -> None:
        scanner = ICMPScanner(timeout=2.0)
        result = scanner.ping("127.0.0.1")
        self.assertEqual(result.status, HostStatus.UP)

    def test_ping_invalid(self) -> None:
        scanner = ICMPScanner(timeout=1.0)
        result = scanner.ping("192.0.2.1")  # TEST-NET-1, should be unreachable
        self.assertIn(result.status, (HostStatus.DOWN, HostStatus.UNKNOWN))

    def test_discover_hosts(self) -> None:
        scanner = ICMPScanner(timeout=2.0, max_workers=2)
        results = scanner.discover_hosts(["127.0.0.1", "127.0.0.2"])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status, HostStatus.UP)  # 127.0.0.1 always up


class TestScanConfig(unittest.TestCase):
    def test_defaults(self) -> None:
        config = ScanConfig()
        self.assertEqual(config.targets, [])
        self.assertEqual(config.ports, [])
        self.assertEqual(config.timeout, 1.0)
        self.assertEqual(config.max_workers, 100)

    def test_custom(self) -> None:
        config = ScanConfig(
            targets=["192.168.1.1"],
            ports=[80, 443],
            timeout=0.5,
            max_workers=10,
        )
        self.assertEqual(len(config.targets), 1)
        self.assertEqual(len(config.ports), 2)


if __name__ == "__main__":
    unittest.main()
