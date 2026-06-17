import pytest
from unittest.mock import patch, MagicMock
from crawler.crawler import WebCrawler
from core.utils import extract_emails, extract_phones, normalize_url, is_internal, is_social


class TestUtils:
    def test_extract_emails_basic(self):
        text = "Contact us at hello@example.com or support@test.org"
        result = extract_emails(text)
        assert "hello@example.com" in result
        assert "support@test.org" in result

    def test_extract_emails_empty(self):
        assert extract_emails("no emails here") == set()

    def test_extract_phones_basic(self):
        text = "Call us at +1-800-555-1234 or 020 7946 0958"
        result = extract_phones(text)
        assert len(result) >= 1

    def test_normalize_url_relative(self):
        result = normalize_url("https://example.com/page", "/about")
        assert result == "https://example.com/about"

    def test_normalize_url_fragment_stripped(self):
        result = normalize_url("https://example.com", "/page#section")
        assert "#section" not in result

    def test_normalize_url_invalid_scheme(self):
        result = normalize_url("https://example.com", "javascript:void(0)")
        assert result is None

    def test_is_internal_same_domain(self):
        assert is_internal("https://example.com", "https://example.com/about") is True

    def test_is_internal_different_domain(self):
        assert is_internal("https://example.com", "https://other.com/page") is False

    def test_is_social_facebook(self):
        assert is_social("https://facebook.com/page") is True

    def test_is_social_internal(self):
        assert is_social("https://example.com") is False


class TestWebCrawler:
    def test_init(self):
        crawler = WebCrawler("https://example.com", depth=2)
        assert crawler.base_url == "https://example.com"
        assert crawler.depth == 2
        assert len(crawler.visited) == 0

    @patch("crawler.crawler.WebCrawler._fetch")
    def test_crawl_single_page(self, mock_fetch):
        mock_fetch.return_value = """
        <html><body>
            <a href="/about">About</a>
            <a href="https://facebook.com/test">Facebook</a>
            <p>Email: test@example.com</p>
        </body></html>
        """
        crawler = WebCrawler("https://example.com", depth=1)
        result = crawler.crawl()
        assert "https://example.com" in result["pages_crawled"]
        assert "test@example.com" in result["emails"]

    @patch("crawler.crawler.WebCrawler._fetch")
    def test_crawl_handles_fetch_failure(self, mock_fetch):
        mock_fetch.return_value = None
        crawler = WebCrawler("https://example.com", depth=1)
        result = crawler.crawl()
        assert result["pages_crawled"] == []
        assert result["emails"] == []
