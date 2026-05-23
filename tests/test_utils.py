import unittest
from scanner.utils import parse_ip_target, parse_port_range, get_service_name


class TestParseIPTarget(unittest.TestCase):
    def test_single_ip(self) -> None:
        self.assertEqual(parse_ip_target("192.168.1.1"), ["192.168.1.1"])

    def test_cidr(self) -> None:
        result = parse_ip_target("192.168.1.0/30")
        self.assertEqual(len(result), 2)
        self.assertIn("192.168.1.1", result)
        self.assertIn("192.168.1.2", result)

    def test_range(self) -> None:
        result = parse_ip_target("10.0.0.1-10.0.0.3")
        self.assertEqual(result, ["10.0.0.1", "10.0.0.2", "10.0.0.3"])

    def test_range_reversed(self) -> None:
        with self.assertRaises(ValueError):
            parse_ip_target("10.0.0.3-10.0.0.1")

    def test_hostname(self) -> None:
        result = parse_ip_target("localhost")
        self.assertEqual(result, ["localhost"])

    def test_empty(self) -> None:
        with self.assertRaises(ValueError):
            parse_ip_target("")

    def test_invalid_cidr(self) -> None:
        with self.assertRaises(ValueError):
            parse_ip_target("not_an_ip/24")


class TestParsePortRange(unittest.TestCase):
    def test_single(self) -> None:
        self.assertEqual(parse_port_range("80"), [80])

    def test_range(self) -> None:
        self.assertEqual(parse_port_range("80-83"), [80, 81, 82, 83])

    def test_list(self) -> None:
        self.assertEqual(parse_port_range("22,80,443"), [22, 80, 443])

    def test_mixed(self) -> None:
        result = parse_port_range("22,80-82,443")
        self.assertEqual(result, [22, 80, 81, 82, 443])

    def test_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            parse_port_range("65536")

    def test_reversed_range(self) -> None:
        with self.assertRaises(ValueError):
            parse_port_range("100-50")

    def test_empty(self) -> None:
        with self.assertRaises(ValueError):
            parse_port_range("")

    def test_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_port_range("abc")


class TestGetServiceName(unittest.TestCase):
    def test_known(self) -> None:
        self.assertEqual(get_service_name(80), "http")
        self.assertEqual(get_service_name(443), "https")
        self.assertEqual(get_service_name(22), "ssh")

    def test_unknown(self) -> None:
        self.assertEqual(get_service_name(65000), "unknown")


if __name__ == "__main__":
    unittest.main()
