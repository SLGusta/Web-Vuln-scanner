# utils/reporter.py
import json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

SEVERITY_COLORS = {
    "Alta": Fore.RED,
    "Média (anomalia de tamanho)": Fore.YELLOW,
    "Baixa (revisar manualmente)": Fore.CYAN,
}

def print_findings(findings: list[dict]):
    if not findings:
        print(Fore.GREEN + "\n[✓] Nenhuma vulnerabilidade detectada nos endpoints testados.")
        return

    print(f"\n{'='*60}")
    print(Fore.RED + f"  {len(findings)} VULNERABILIDADE(S) ENCONTRADA(S)")
    print(f"{'='*60}\n")

    for i, f in enumerate(findings, 1):
        color = SEVERITY_COLORS.get(f.get("confidence", ""), Fore.WHITE)
        print(color + f"[{i}] {f['type']} — Confiança: {f.get('confidence', 'N/A')}")
        print(f"    Endpoint : {f['endpoint']}")
        print(f"    Parâmetro: {f['param']}")
        print(f"    Payload  : {f['payload']}")
        print(f"    Método   : {f['method']} | Status HTTP: {f['status']}")
        if f.get("db_engine"):
            print(f"    Motor DB : {f['db_engine']}")
        if f.get("signature"):
            print(f"    Assinatura: {f['signature']}")
        print(f"    Evidência:")
        print(Style.DIM + f"    {f['evidence'][:200].strip()}")
        print()

def save_json(findings: list[dict], target: str):
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = {
        "scanner":    "web-vuln-scanner v1.0",
        "target":     target,
        "timestamp":  datetime.now().isoformat(),
        "total":      len(findings),
        "findings":   findings,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(Fore.CYAN + f"\n[+] Relatório salvo em: {filename}")