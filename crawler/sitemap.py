import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from core.config import OUTPUT_DIR
from core.logger import get_logger

logger = get_logger(__name__)


def generate_sitemap(pages: list[str], output_dir: str = OUTPUT_DIR) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = page
        ET.SubElement(url_el, "lastmod").text = datetime.utcnow().strftime("%Y-%m-%d")
        ET.SubElement(url_el, "changefreq").text = "monthly"
        ET.SubElement(url_el, "priority").text = "0.5"

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")

    output_path = Path(output_dir) / "sitemap.xml"
    tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
    logger.info(f"Sitemap saved to {output_path}")
    return str(output_path)
