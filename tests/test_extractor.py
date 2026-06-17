import pytest
from unittest.mock import patch, MagicMock
from crawler.extractor import ContactExtractor


class TestContactExtractor:
    @patch("crawler.extractor.requests.get")
    def test_extract_emails_and_phones(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <html><body>
            <p>Email: sales@company.com</p>
            <p>Phone: +1-800-555-1234</p>
            <a href="https://twitter.com/company">Twitter</a>
        </body></html>
        """
        mock_get.return_value = mock_resp
        extractor = ContactExtractor("https://example.com")
        result = extractor.extract()
        assert "sales@company.com" in result["emails"]
        assert len(result["phones"]) >= 1

    @patch("crawler.extractor.requests.get")
    def test_extract_social_links(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <html><body>
            <a href="https://linkedin.com/company/test">LinkedIn</a>
            <a href="https://github.com/test">GitHub</a>
        </body></html>
        """
        mock_get.return_value = mock_resp
        extractor = ContactExtractor("https://example.com")
        result = extractor.extract()
        assert any("linkedin.com" in s for s in result["social_links"])
        assert any("github.com" in s for s in result["social_links"])

    @patch("crawler.extractor.requests.get")
    def test_extract_handles_failure(self, mock_get):
        mock_get.side_effect = Exception("Timeout")
        extractor = ContactExtractor("https://example.com")
        result = extractor.extract()
        assert result == {}
