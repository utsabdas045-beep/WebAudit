import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from core.config import DEFAULT_THREADS, DEFAULT_TIMEOUT, DEFAULT_PORTS
from core.logger import get_logger

logger = get_logger(__name__)

COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 8888: "HTTP-Alt2", 27017: "MongoDB",
}


def scan_port(host: str, port: int, timeout: int) -> dict | None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            service = COMMON_SERVICES.get(port, "Unknown")
            try:
                banner_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                banner_sock.settimeout(2)
                banner_sock.connect((host, port))
                banner = banner_sock.recv(256).decode(errors="ignore").strip()
                banner_sock.close()
            except Exception:
                banner = ""
            return {"port": port, "service": service, "banner": banner}
    except Exception as e:
        logger.debug(f"Error scanning {host}:{port} - {e}")
    return None


class PortScanner:
    def __init__(self, host: str, ports: list[int] = None, threads: int = DEFAULT_THREADS, timeout: int = DEFAULT_TIMEOUT):
        self.host = host
        self.ports = ports or DEFAULT_PORTS
        self.threads = threads
        self.timeout = timeout

    def scan(self) -> dict:
        open_ports = []
        start = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[+] Scanning ports...", total=len(self.ports))

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(scan_port, self.host, p, self.timeout): p for p in self.ports}
                for future in as_completed(futures):
                    progress.advance(task)
                    result = future.result()
                    if result:
                        open_ports.append(result)

        open_ports.sort(key=lambda x: x["port"])
        duration = round(time.time() - start, 2)
        return {
            "host": self.host,
            "open_ports": open_ports,
            "total_scanned": len(self.ports),
            "duration": duration,
        }
