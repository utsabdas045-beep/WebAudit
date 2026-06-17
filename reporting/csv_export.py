import csv
from pathlib import Path
from datetime import datetime

from core.config import OUTPUT_DIR
from core.logger import get_logger

logger = get_logger(__name__)


def export_csv(data: dict, output_dir: str = OUTPUT_DIR) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    domain = data.get("base_url", "report").replace("https://", "").replace("http://", "").replace("/", "_")
    filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = Path(output_dir) / filename

    rows = []

    for email in data.get("emails", []):
        rows.append({"type": "Email", "value": email, "source": data.get("base_url", "")})

    for phone in data.get("phones", []):
        rows.append({"type": "Phone", "value": phone, "source": data.get("base_url", "")})

    for link in data.get("social_links", []):
        rows.append({"type": "Social", "value": link, "source": data.get("base_url", "")})

    port_data = data.get("port_scan", {})
    for port_info in port_data.get("open_ports", []):
        rows.append({
            "type": "Open Port",
            "value": f"{port_info['port']}/{port_info['service']}",
            "source": port_data.get("host", ""),
        })

    header_data = data.get("headers", {})
    for h in header_data.get("missing_headers", []):
        rows.append({"type": "Missing Header", "value": h, "source": data.get("base_url", "")})

    if not rows:
        rows.append({"type": "N/A", "value": "No data found", "source": ""})

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["type", "value", "source"])
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"CSV report saved to {output_path}")
    return str(output_path)
