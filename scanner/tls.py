import ssl
import socket
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)


class TLSAnalyzer:
    def __init__(self, host: str, port: int = 443, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout

    def analyze(self) -> dict:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert()
                    tls_version = ssock.version()
                    cipher = ssock.cipher()
        except ssl.SSLCertVerificationError as e:
            return {"host": self.host, "error": f"Certificate verification failed: {e}", "valid": False}
        except Exception as e:
            logger.error(f"TLS analysis failed for {self.host}: {e}")
            return {"host": self.host, "error": str(e), "valid": False}

        if not cert:
            return {
                "host": self.host,
                "valid": False,
                "error": "No certificate data retrieved.",
                "warnings": ["Could not parse TLS certificate details."]
            }

        subject = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))

        not_after_str = cert.get("notAfter", "")
        not_before_str = cert.get("notBefore", "")

        try:
            not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
            not_before = datetime.strptime(not_before_str, "%b %d %H:%M:%S %Y %Z")
            days_remaining = (not_after - datetime.utcnow()).days
            expired = days_remaining < 0
        except Exception:
            not_after = not_before = None
            days_remaining = None
            expired = None

        san = [v for _, v in cert.get("subjectAltName", [])]

        warnings = []
        if expired:
            warnings.append("Certificate has expired!")
        elif days_remaining is not None and days_remaining < 30:
            warnings.append(f"Certificate expires in {days_remaining} days!")
        if tls_version in ("TLSv1", "TLSv1.1"):
            warnings.append(f"{tls_version} is deprecated and insecure.")

        return {
            "host": self.host,
            "valid": True,
            "subject": subject,
            "issuer": issuer,
            "not_before": str(not_before),
            "not_after": str(not_after),
            "days_remaining": days_remaining,
            "expired": expired,
            "tls_version": tls_version,
            "cipher": cipher[0] if cipher else None,
            "san": san,
            "warnings": warnings,
        }
