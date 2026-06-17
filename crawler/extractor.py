import requests
from bs4 import BeautifulSoup

from core.config import USER_AGENT, DEFAULT_TIMEOUT
from core.utils import extract_emails, extract_phones, is_social, normalize_url
from core.logger import get_logger

logger = get_logger(__name__)


class ContactExtractor:
    def __init__(self, url: str, timeout: int = DEFAULT_TIMEOUT):
        self.url = url
        self.timeout = timeout
        self.headers = {"User-Agent": USER_AGENT}

    def _fetch(self, url: str) -> str | None:
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            return resp.text
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return None

    def extract(self) -> dict:
        html = self._fetch(self.url)
        if not html:
            return {}

        emails = extract_emails(html)
        phones = extract_phones(html)
        social = set()

        soup = BeautifulSoup(html, "lxml")
        for tag in soup.find_all("a", href=True):
            url = normalize_url(self.url, tag["href"])
            if url and is_social(url):
                social.add(url)

        return {
            "url": self.url,
            "emails": list(emails),
            "phones": list(phones),
            "social_links": list(social),
        }
