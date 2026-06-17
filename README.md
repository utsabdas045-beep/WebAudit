# 🔍 WebAudit

**Website Reconnaissance and Security Auditing Toolkit**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/yourusername/webaudit/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/webaudit/actions)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://kali.org)

> A command-line security auditing tool built in Python for authorized website reconnaissance, contact extraction, port scanning, and security analysis.

---

## ⚠️ Disclaimer

**For authorized and educational use only.**  
Never run WebAudit against websites you do not own or have explicit permission to test.  
The author is not responsible for any misuse of this tool.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🕷️ **Website Crawler** | Crawl internal links with configurable depth, respects `robots.txt` |
| 📧 **Contact Extractor** | Extract emails, phone numbers, social media links |
| 🔌 **Port Scanner** | Multithreaded TCP port scanning with service detection |
| 🛡️ **Header Analyzer** | Check for missing security headers with a scored report |
| 🔒 **TLS Analyzer** | Analyze SSL/TLS certificates, expiry, and cipher suites |
| 📄 **Report Generator** | Generate HTML, JSON, and CSV reports + XML sitemap |

---

## 🚀 Installation

**Tested on:** Kali Linux, Ubuntu 22.04+, Debian 12, Parrot OS

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/webaudit.git
cd webaudit
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install as a command

```bash
pip install -e .
```

---

## 🖥️ Usage

### Full Audit (recommended)

```bash
python main.py full https://example.com
```

Runs crawl → port scan → header analysis → TLS check → generates HTML/JSON/CSV reports.

---

### Individual Commands

#### Crawl a website
```bash
python main.py crawl https://example.com
python main.py crawl https://example.com --depth 5
```

#### Extract emails & contacts
```bash
python main.py emails https://example.com
```

#### Scan ports
```bash
python main.py ports example.com
python main.py ports example.com --ports 22,80,443,8080
```

#### Analyze security headers
```bash
python main.py headers https://example.com
```

#### Inspect TLS/SSL certificate
```bash
python main.py tls example.com
```

---

## 📁 Project Structure

```
webaudit/
├── main.py                 # CLI entry point
├── requirements.txt
├── setup.py
│
├── crawler/
│   ├── crawler.py          # Website crawler with robots.txt support
│   ├── extractor.py        # Email/phone/social extractor
│   └── sitemap.py          # XML sitemap generator
│
├── scanner/
│   ├── port_scanner.py     # Multithreaded TCP port scanner
│   ├── headers.py          # Security header analyzer
│   └── tls.py              # SSL/TLS certificate analyzer
│
├── reporting/
│   ├── html_report.py      # HTML report (Jinja2 template)
│   ├── csv_export.py       # CSV export
│   └── json_export.py      # JSON export
│
├── core/
│   ├── config.py           # Global configuration
│   ├── logger.py           # File-based logger
│   └── utils.py            # Shared utility functions
│
├── templates/
│   └── report.html         # Dark-theme HTML report template
│
├── tests/                  # pytest unit tests
├── output/reports/         # Generated reports saved here
└── logs/                   # Log files
```

---

## 📊 Sample Output

```
╭─────────────────────────────────────────╮
│  WebAudit v1.0                          │
│  Website Reconnaissance & Security Tool │
╰─────────────────────────────────────────╯

[+] Starting crawl: https://example.com
[+] Crawling: https://example.com/about
[+] Crawling: https://example.com/contact

┌─────────────────────┬────────┐
│ Metric              │ Value  │
├─────────────────────┼────────┤
│ Pages Crawled       │ 14     │
│ Internal Links      │ 32     │
│ Emails Found        │ 4      │
│ Phones Found        │ 2      │
│ Social Links        │ 5      │
│ Duration            │ 8.43s  │
└─────────────────────┴────────┘

[+] Security Score: 75/100
[+] Open Ports: 80, 443
[+] TLS: TLSv1.3 | Days Remaining: 87
[+] Reports Generated: output/reports/
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

---

## 🛠️ Tech Stack

- **Python 3.12+**
- `requests` — HTTP client
- `beautifulsoup4` + `lxml` — HTML parsing
- `rich` — Terminal UI
- `jinja2` — HTML report templating
- `socket` / `ssl` — Port scanning & TLS analysis
- `concurrent.futures` — Multithreaded scanning
- `pytest` — Unit testing

---

## 📖 What I Learned Building This

- Web scraping with BeautifulSoup and URL normalization
- Multithreaded network programming with `ThreadPoolExecutor`
- SSL/TLS internals using Python's `ssl` module
- Security header analysis and OWASP best practices
- CLI design with `argparse` and `rich`
- Report generation with Jinja2 templates
- Writing unit tests with `pytest` and mocking

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repository
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request
