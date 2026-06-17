import json
from pathlib import Path
from datetime import datetime

from core.config import OUTPUT_DIR
from core.logger import get_logger

logger = get_logger(__name__)


def export_json(data: dict, output_dir: str = OUTPUT_DIR) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    domain = data.get("base_url", "report").replace("https://", "").replace("http://", "").replace("/", "_")
    filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = Path(output_dir) / filename

    export_data = {
        "generated_at": datetime.now().isoformat(),
        **data,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)

    logger.info(f"JSON report saved to {output_path}")
    return str(output_path)
