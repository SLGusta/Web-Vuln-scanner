import argparse

from core.http_client import HTTPClient
from modules import sqli, xss, traversal
from utils import reporter


def main():
    parser = argparse.ArgumentParser(
        description="web-vuln-scanner — Scanner educacional OWASP Top 10"
    )

    parser.add_argument(
        "url",
        help="URL base do alvo (ex: http://localhost/dvwa)"
    )

    parser.add_argument(
        "--cookie",
        default="",
        help="Cookie de sessão (ex: PHPSESSID=abc123; security=low)"
    )

    parser.add_argument(
        "--output",
        action="store_true",
        help="Salvar relatório JSON"
    )

    args = parser.parse_args()

    headers = {}

    if args.cookie:
        headers["Cookie"] = args.cookie

    client = HTTPClient(
        base_url=args.url,
        headers=headers
    )

    all_findings = []

    print(f"\n[*] Alvo: {args.url}")
    print("[*] Iniciando varredura...\n")

    # SQL Injection
    print("[MODULE] SQL Injection")
    findings_sqli = sqli.run(
        client,
        endpoint="vulnerabilities/sqli/",
        params={
            "id": "1",
            "Submit": "Submit"
        },
        method="GET"
    )
    all_findings.extend(findings_sqli)

    # Reflected XSS
    print("\n[MODULE] Reflected XSS")
    findings_xss = xss.run(
        client,
        endpoint="vulnerabilities/xss_r/",
        params={
            "name": "test"
        },
        method="GET"
    )
    all_findings.extend(findings_xss)

    # Directory Traversal
    print("\n[MODULE] Directory Traversal")
    findings_traversal = traversal.run(
        client,
        endpoint="vulnerabilities/fi/",
        param_name="page"
    )
    all_findings.extend(findings_traversal)

    # Relatório
    reporter.print_findings(all_findings)

    if args.output:
        reporter.save_json(
            all_findings,
            args.url
        )


if __name__ == "__main__":
    main()