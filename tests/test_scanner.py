import pytest
from unittest.mock import patch, MagicMock
from scanner.port_scanner import PortScanner, scan_port
from scanner.headers import HeaderAnalyzer


class TestPortScanner:
    def test_init_default_ports(self):
        scanner = PortScanner("example.com")
        assert scanner.host == "example.com"
        assert len(scanner.ports) > 0

    def test_init_custom_ports(self):
        scanner = PortScanner("example.com", ports=[80, 443])
        assert scanner.ports == [80, 443]

    @patch("scanner.port_scanner.socket.socket")
    def test_scan_port_open(self, mock_socket):
        instance = MagicMock()
        instance.connect_ex.return_value = 0
        instance.recv.return_value = b"HTTP/1.1 200 OK"
        mock_socket.return_value = instance
        result = scan_port("example.com", 80, 5)
        assert result is not None
        assert result["port"] == 80

    @patch("scanner.port_scanner.socket.socket")
    def test_scan_port_closed(self, mock_socket):
        instance = MagicMock()
        instance.connect_ex.return_value = 1
        mock_socket.return_value = instance
        result = scan_port("example.com", 9999, 5)
        assert result is None


class TestHeaderAnalyzer:
    @patch("scanner.headers.requests.get")
    def test_analyze_with_all_headers(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "geolocation=()",
        }
        mock_get.return_value = mock_resp
        analyzer = HeaderAnalyzer("https://example.com")
        result = analyzer.analyze()
        assert result["score"] == 100
        assert len(result["missing_headers"]) == 0

    @patch("scanner.headers.requests.get")
    def test_analyze_with_no_headers(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        mock_get.return_value = mock_resp
        analyzer = HeaderAnalyzer("https://example.com")
        result = analyzer.analyze()
        assert result["score"] == 0
        assert len(result["missing_headers"]) == 6

    @patch("scanner.headers.requests.get")
    def test_analyze_handles_exception(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        analyzer = HeaderAnalyzer("https://example.com")
        result = analyzer.analyze()
        assert "error" in result
