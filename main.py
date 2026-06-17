#!/usr/bin/env python3
"""
WebAudit - Website Reconnaissance and Security Auditing Toolkit
"""

import argparse
import sys
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from crawler.crawler import WebCrawler
from crawler.extractor import ContactExtractor
from crawler.sitemap import generate_sitemap
from scanner.port_scanner import PortScanner
from scanner.headers import HeaderAnalyzer
from scanner.tls import TLSAnalyzer
from reporting.html_report import generate_html_report
from reporting.csv_export import export_csv
from reporting.json_export import export_json
from core.config import DEFAULT_DEPTH, DEFAULT_TIMEOUT

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold green]WebAudit[/bold green] [white]v1.0[/white]\n"
        "[dim]Website Reconnaissance & Security Auditing Toolkit[/dim]\n"
        "[dim red]For authorized testing only[/dim red]",
        border_style="green"
    ))


def get_host(url: str) -> str:
    return urlparse(url).netloc or url


def ensure_scheme(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def cmd_crawl(args):
    url = ensure_scheme(args.url)
    console.print(f"\n[bold green][+][/bold green] Starting crawl: [cyan]{url}[/cyan]")
    crawler = WebCrawler(url, depth=args.depth, timeout=args.timeout)
    result = crawler.crawl()

    table = Table(title="Crawl Results", border_style="green")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Pages Crawled", str(len(result["pages_crawled"])))
    table.add_row("Internal Links", str(len(result["internal_links"])))
    table.add_row("Emails Found", str(len(result["emails"])))
    table.add_row("Phones Found", str(len(result["phones"])))
    table.add_row("Social Links", str(len(result["social_links"])))
    table.add_row("Contact Pages", str(len(result["contact_pages"])))
    table.add_row("Duration", f"{result['duration']}s")
    console.print(table)

    sitemap_path = generate_sitemap(result["pages_crawled"])
    console.print(f"\n[green][+][/green] Sitemap saved: [dim]{sitemap_path}[/dim]")


def cmd_emails(args):
    url = ensure_scheme(args.url)
    console.print(f"\n[bold green][+][/bold green] Extracting contacts from: [cyan]{url}[/cyan]")
    extractor = ContactExtractor(url, timeout=args.timeout)
    result = extractor.extract()

    if result.get("emails"):
        console.print(f"\n[green][+] Found {len(result['emails'])} email(s):[/green]")
        for e in result["emails"]:
            console.print(f"  [cyan]{e}[/cyan]")

    if result.get("phones"):
        console.print(f"\n[green][+] Found {len(result['phones'])} phone(s):[/green]")
        for p in result["phones"]:
            console.print(f"  [cyan]{p}[/cyan]")

    if result.get("social_links"):
        console.print(f"\n[green][+] Found {len(result['social_links'])} social link(s):[/green]")
        for s in result["social_links"]:
            console.print(f"  [cyan]{s}[/cyan]")

    export_json({"base_url": url, **result})
    export_csv({"base_url": url, **result})


def cmd_ports(args):
    host = get_host(args.host)
    ports = None
    if args.ports:
        try:
            ports = [int(p.strip()) for p in args.ports.split(",")]
        except ValueError:
            console.print("[red]Invalid port list. Use comma-separated integers.[/red]")
            sys.exit(1)

    console.print(f"\n[bold green][+][/bold green] Scanning ports on: [cyan]{host}[/cyan]")
    scanner = PortScanner(host, ports=ports, timeout=args.timeout)
    result = scanner.scan()

    if result["open_ports"]:
        table = Table(title=f"Open Ports on {host}", border_style="cyan")
        table.add_column("Port", style="bold cyan")
        table.add_column("Service", style="white")
        table.add_column("Banner", style="dim")
        for p in result["open_ports"]:
            table.add_row(str(p["port"]), p["service"], p["banner"][:60] if p["banner"] else "-")
        console.print(table)
    else:
        console.print("[yellow][!] No open ports found in the specified range.[/yellow]")

    console.print(f"\n[green][+][/green] Scanned {result['total_scanned']} ports in {result['duration']}s")


def cmd_headers(args):
    url = ensure_scheme(args.url)
    console.print(f"\n[bold green][+][/bold green] Analyzing headers: [cyan]{url}[/cyan]")
    analyzer = HeaderAnalyzer(url, timeout=args.timeout)
    result = analyzer.analyze()

    if "error" in result:
        console.print(f"[red][!] Error: {result['error']}[/red]")
        return

    table = Table(title="Security Headers Analysis", border_style="blue")
    table.add_column("Header", style="white")
    table.add_column("Status")
    table.add_column("Value", style="dim")

    for h, v in result["present_headers"].items():
        table.add_row(h, "[green]✔ Present[/green]", v[:60])
    for h in result["missing_headers"]:
        table.add_row(h, "[red]✘ Missing[/red]", "-")

    console.print(table)
    console.print(f"\n[bold]Security Score:[/bold] [{'green' if result['score'] > 60 else 'yellow' if result['score'] > 30 else 'red'}]{result['score']}/{result['max_score']}[/]")

    if result["recommendations"]:
        console.print("\n[yellow][!] Recommendations:[/yellow]")
        for rec in result["recommendations"]:
            console.print(f"  [dim]→[/dim] {rec}")


def cmd_tls(args):
    host = get_host(args.host)
    console.print(f"\n[bold green][+][/bold green] Analyzing TLS/SSL: [cyan]{host}[/cyan]")
    analyzer = TLSAnalyzer(host)
    result = analyzer.analyze()

    if not result.get("valid"):
        console.print(f"[red][!] TLS Error: {result.get('error')}[/red]")
        return

    table = Table(title=f"TLS Certificate: {host}", border_style="blue")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Subject", result["subject"].get("commonName", "-"))
    table.add_row("Issuer", result["issuer"].get("organizationName", "-"))
    table.add_row("TLS Version", result["tls_version"])
    table.add_row("Cipher", result["cipher"] or "-")
    table.add_row("Valid From", str(result["not_before"]))
    table.add_row("Expires", str(result["not_after"]))
    days = result.get("days_remaining")
    color = "green" if days and days > 30 else "red"
    table.add_row("Days Remaining", f"[{color}]{days}[/{color}]")
    console.print(table)

    if result.get("san"):
        console.print(f"\n[cyan]SANs:[/cyan] {', '.join(result['san'][:5])}")

    if result["warnings"]:
        for w in result["warnings"]:
            console.print(f"[red][!] {w}[/red]")


def cmd_full(args):
    url = ensure_scheme(args.url)
    host = get_host(url)
    console.print(f"\n[bold green][+][/bold green] Running full audit on: [cyan]{url}[/cyan]\n")

    # Crawl
    console.rule("[green]Crawling[/green]")
    crawler = WebCrawler(url, depth=args.depth, timeout=args.timeout)
    crawl_data = crawler.crawl()
    console.print(f"[green][+][/green] Pages: {len(crawl_data['pages_crawled'])} | Emails: {len(crawl_data['emails'])} | Phones: {len(crawl_data['phones'])}")

    # Port Scan
    console.rule("[cyan]Port Scan[/cyan]")
    scanner = PortScanner(host, timeout=args.timeout)
    port_data = scanner.scan()
    open_ports = [str(p["port"]) for p in port_data["open_ports"]]
    console.print(f"[green][+][/green] Open Ports: {', '.join(open_ports) if open_ports else 'None'}")

    # Headers
    console.rule("[blue]Security Headers[/blue]")
    header_analyzer = HeaderAnalyzer(url, timeout=args.timeout)
    header_data = header_analyzer.analyze()
    if "error" not in header_data:
        console.print(f"[green][+][/green] Security Score: {header_data['score']}/{header_data['max_score']}")

    # TLS
    console.rule("[blue]TLS Analysis[/blue]")
    tls_analyzer = TLSAnalyzer(host)
    tls_data = tls_analyzer.analyze()
    if tls_data.get("valid"):
        console.print(f"[green][+][/green] TLS: {tls_data['tls_version']} | Days Remaining: {tls_data.get('days_remaining')}")
    else:
        console.print(f"[red][!][/red] TLS Error: {tls_data.get('error')}")

    # Sitemap
    sitemap_path = generate_sitemap(crawl_data["pages_crawled"])

    # Reports
    console.rule("[yellow]Generating Reports[/yellow]")
    report_data = {
        **crawl_data,
        "port_scan": port_data,
        "headers": header_data if "error" not in header_data else None,
        "tls": tls_data,
    }

    html_path = generate_html_report(report_data)
    json_path = export_json(report_data)
    csv_path = export_csv(report_data)

    console.print(f"\n[bold green][+] Reports Generated:[/bold green]")
    console.print(f"  [dim]HTML:[/dim] {html_path}")
    console.print(f"  [dim]JSON:[/dim] {json_path}")
    console.print(f"  [dim]CSV:[/dim]  {csv_path}")
    console.print(f"  [dim]Sitemap:[/dim] {sitemap_path}")


def main():
    banner()

    parser = argparse.ArgumentParser(
        prog="webaudit",
        description="Website Reconnaissance and Security Auditing Toolkit",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # crawl
    p_crawl = subparsers.add_parser("crawl", help="Crawl a website")
    p_crawl.add_argument("url", help="Target URL (e.g. https://example.com)")
    p_crawl.add_argument("--depth", type=int, default=DEFAULT_DEPTH, help="Crawl depth (default: 3)")

    # emails
    p_emails = subparsers.add_parser("emails", help="Extract contact info")
    p_emails.add_argument("url", help="Target URL")

    # ports
    p_ports = subparsers.add_parser("ports", help="Scan open ports")
    p_ports.add_argument("host", help="Target host or URL")
    p_ports.add_argument("--ports", help="Comma-separated port list (default: common ports)")

    # headers
    p_headers = subparsers.add_parser("headers", help="Analyze security headers")
    p_headers.add_argument("url", help="Target URL")

    # tls
    p_tls = subparsers.add_parser("tls", help="Analyze TLS/SSL certificate")
    p_tls.add_argument("host", help="Target host or URL")

    # full
    p_full = subparsers.add_parser("full", help="Run full audit and generate report")
    p_full.add_argument("url", help="Target URL")
    p_full.add_argument("--depth", type=int, default=DEFAULT_DEPTH, help="Crawl depth (default: 3)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Attach timeout to all sub-commands
    if not hasattr(args, "timeout"):
        args.timeout = DEFAULT_TIMEOUT

    commands = {
        "crawl": cmd_crawl,
        "emails": cmd_emails,
        "ports": cmd_ports,
        "headers": cmd_headers,
        "tls": cmd_tls,
        "full": cmd_full,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red][!] Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
