import requests
from core.config import SECURITY_HEADERS, HEADER_WEIGHTS, HEADER_RECOMMENDATIONS, USER_AGENT, DEFAULT_TIMEOUT
from core.logger import get_logger

logger = get_logger(__name__)


class HeaderAnalyzer:
    def __init__(self, url: str, timeout: int = DEFAULT_TIMEOUT):
        self.url = url
        self.timeout = timeout

    def analyze(self) -> dict:
        try:
            resp = requests.get(
                self.url,
                headers={"User-Agent": USER_AGENT},
                timeout=self.timeout,
                allow_redirects=True,
            )
        except Exception as e:
            logger.error(f"Failed to fetch headers for {self.url}: {e}")
            return {"error": str(e)}

        present = {}
        missing = []
        recommendations = []
        score = 0

        for header in SECURITY_HEADERS:
            value = resp.headers.get(header)
            if value:
                present[header] = value
                score += HEADER_WEIGHTS.get(header, 0)
            else:
                missing.append(header)
                recommendations.append(HEADER_RECOMMENDATIONS.get(header, ""))

        return {
            "url": self.url,
            "status_code": resp.status_code,
            "present_headers": present,
            "missing_headers": missing,
            "recommendations": [r for r in recommendations if r],
            "score": score,
            "max_score": sum(HEADER_WEIGHTS.values()),
        }
