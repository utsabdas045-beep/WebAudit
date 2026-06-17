from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from core.config import OUTPUT_DIR
from core.logger import get_logger

logger = get_logger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def generate_html_report(data: dict, output_dir: str = OUTPUT_DIR) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html")

    data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = template.render(**data)

    domain = data.get("base_url", "report").replace("https://", "").replace("http://", "").replace("/", "_")
    filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_path = Path(output_dir) / filename
    output_path.write_text(html, encoding="utf-8")
    logger.info(f"HTML report saved to {output_path}")
    return str(output_path)
