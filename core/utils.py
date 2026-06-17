import re
from urllib.parse import urlparse, urljoin
from core.config import SOCIAL_DOMAINS


def normalize_url(base: str, href: str) -> str | None:
    try:
        full = urljoin(base, href)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            return None
        clean = parsed._replace(fragment="").geturl()
        return clean.rstrip("/")
    except Exception:
        return None


def get_domain(url: str) -> str:
    return urlparse(url).netloc


def is_internal(base_url: str, url: str) -> bool:
    return get_domain(base_url) == get_domain(url)


def is_social(url: str) -> bool:
    domain = get_domain(url)
    return any(s in domain for s in SOCIAL_DOMAINS)


def extract_emails(text: str) -> set[str]:
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    found = re.findall(pattern, text)
    return {e.lower() for e in found}


def extract_phones(text: str) -> set[str]:
    pattern = r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}"
    found = re.findall(pattern, text)
    valid = set()
    for p in found:
        digits = re.sub(r"\D", "", p)
        if 7 <= len(digits) <= 15:
            valid.add(p.strip())
    return valid


def is_contact_page(url: str) -> bool:
    keywords = ["contact", "about", "reach", "connect", "support", "help", "enquiry"]
    return any(k in url.lower() for k in keywords)
