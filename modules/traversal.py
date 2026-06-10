from core.http_client import HTTPClient

def carregar_payloads(path: str = "payloads/traversal.txt") -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
    
# Assinaturas  de conteudos de arquivos  sensíveis
SENSITIVE_SIGNATURES = [
    "root:x:0:0",             # /etc/passwd Linux
    "[boot loader]",          # win.ini Windows
    "[fonts]",                # win.ini Windows
    "[extensions]",           # win.ini
    "# localhost",            # /etc/hosts
    "microsoft windows",      # win.ini
    "shadow",                 # /etc/shadow (parcial)
    "daemon:x:",              # /etc/passwd
]

def contains_sensitive_content(text: str) -> tuple[bool, str]:
    text_lower = text.lower()
    for sig in SENSITIVE_SIGNATURES:
        if sig.lower() in text_lower:
            return True, sig
    return False, ""

def run(client: HTTPClient, endpoint: str, param_name: str) -> list[dict]:

    """
    Executa fuzzing de Directory Traversal em um parâmetro de caminho.

    Args:
        client:     instância do HTTPClient
        endpoint:   path do endpoint (ex: "vulnerabilities/fi/")
        param_name: nome do parâmetro de arquivo (ex: "page")

    Returns:
        Lista de achados com o arquivo acessado e evidência.
    """

    findings = []
    payloads = carregar_payloads()
    baseline = client.get(endpoint, params={param_name: "index.php"})
    baseline_lenght = len(baseline.text) if baseline else 0

    print(f" [TRAVERSAl] Testando parâmetros: '{param_name}' em {endpoint}")

    for payload in payloads:
        response = client.get(endpoint, params={param_name: payload})

        if response is None or response.status_code in [400, 403, 404, 500]:
            continue

        is_sensitive,signature = contains_sensitive_content(response.text)
        length_delta = abs(len(response.text) - baseline_lenght)

        # Evidência Forte: conteúdo sensível detectado
        if is_sensitive:
            finding = {
                "type":       "Directory Traversal",
                "endpoint":   endpoint,
                "param":      param_name,
                "payload":    payload,
                "method":     "GET",
                "status":     response.status_code,
                "evidence":   response.text[:400],
                "signature":  signature,
                "confidence": "Alta",
            }
            findings.append(finding)
            print(f"    [?] Anomalia | payload='{payload}' | delta={length_delta}B — verificar manualmente")
    return findings