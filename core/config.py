DEFAULT_TIMEOUT = 10
DEFAULT_DEPTH = 3
DEFAULT_THREADS = 50
DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443, 8888, 27017]

SOCIAL_DOMAINS = [
    "facebook.com", "twitter.com", "x.com", "linkedin.com",
    "instagram.com", "youtube.com", "github.com", "tiktok.com",
    "pinterest.com", "reddit.com", "telegram.org", "wa.me"
]

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]

HEADER_WEIGHTS = {
    "Content-Security-Policy": 30,
    "Strict-Transport-Security": 25,
    "X-Frame-Options": 15,
    "X-Content-Type-Options": 15,
    "Referrer-Policy": 10,
    "Permissions-Policy": 5,
}

HEADER_RECOMMENDATIONS = {
    "Content-Security-Policy": "Add CSP header to prevent XSS and data injection attacks.",
    "Strict-Transport-Security": "Enable HSTS to enforce HTTPS connections.",
    "X-Frame-Options": "Set X-Frame-Options to DENY or SAMEORIGIN to prevent clickjacking.",
    "X-Content-Type-Options": "Set X-Content-Type-Options: nosniff to prevent MIME sniffing.",
    "Referrer-Policy": "Set Referrer-Policy to control referrer information sent with requests.",
    "Permissions-Policy": "Use Permissions-Policy to restrict access to browser features.",
}

USER_AGENT = "WebAudit/1.0 (Security Auditing Tool; Educational)"
OUTPUT_DIR = "output/reports"
LOG_DIR = "logs"
