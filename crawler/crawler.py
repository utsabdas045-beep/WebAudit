import time
import urllib.robotparser
from collections import deque
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from core.config import DEFAULT_DEPTH, DEFAULT_TIMEOUT, USER_AGENT
from core.logger import get_logger
from core.utils import normalize_url, is_internal, is_social, is_contact_page, extract_emails, extract_phones

logger = get_logger(__name__)


class WebCrawler:
    def __init__(self, base_url: str, depth: int = DEFAULT_DEPTH, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.depth = depth
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.visited: set[str] = set()
        self.internal_links: set[str] = set()
        self.emails: set[str] = set()
        self.phones: set[str] = set()
        self.social_links: set[str] = set()
        self.contact_pages: set[str] = set()
        self.pages_crawled: list[str] = []
        self._robots = self._load_robots()

    def _load_robots(self) -> urllib.robotparser.RobotFileParser:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.set_url(f"{self.base_url}/robots.txt")
            rp.read()
        except Exception:
            pass
        return rp

    def _allowed(self, url: str) -> bool:
        try:
            return self._robots.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    def _fetch(self, url: str) -> str | None:
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if "text/html" in resp.headers.get("Content-Type", ""):
                return resp.text
        except Exception as e:
            logger.debug(f"Fetch failed {url}: {e}")
        return None

    def _parse_links(self, html: str, current_url: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        links = []
        for tag in soup.find_all("a", href=True):
            url = normalize_url(current_url, tag["href"])
            if url:
                links.append(url)
        return links

    def crawl(self) -> dict:
        start = time.time()
        queue = deque([(self.base_url, 0)])

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[+] Crawling website...", total=None)

            while queue:
                url, current_depth = queue.popleft()

                if url in self.visited or current_depth > self.depth:
                    continue
                if not self._allowed(url):
                    logger.debug(f"Blocked by robots.txt: {url}")
                    continue

                self.visited.add(url)
                html = self._fetch(url)
                if not html:
                    continue

                self.pages_crawled.append(url)
                progress.update(task, description=f"[+] Crawling: {url[:60]}")

                self.emails.update(extract_emails(html))
                self.phones.update(extract_phones(html))

                for link in self._parse_links(html, url):
                    if is_internal(self.base_url, link):
                        self.internal_links.add(link)
                        if link not in self.visited:
                            queue.append((link, current_depth + 1))
                        if is_contact_page(link):
                            self.contact_pages.add(link)
                    elif is_social(link):
                        self.social_links.add(link)

        duration = round(time.time() - start, 2)
        return {
            "base_url": self.base_url,
            "pages_crawled": self.pages_crawled,
            "internal_links": list(self.internal_links),
            "emails": list(self.emails),
            "phones": list(self.phones),
            "social_links": list(self.social_links),
            "contact_pages": list(self.contact_pages),
            "duration": duration,
        }
