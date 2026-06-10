from core.http_client import HTTPClient

def carregar_payloads(path: str = "payloads/xss.txt") -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def payload_reflected(response_text: str, payload: str) -> bool:

    """
    Função para verificar se o payload está presente SEM codificação HTML.
    """

    # Se o payload bruto está na resposta -> retorna sem escape -> xss
    if payload in response_text:
        return True
    
    # Verificar retorno parcial: só a tag <script> sem encode
    dangerous_tag = ["<script>", "<img ", "<svg ", "<iframe ", "<body "]
    for tag in dangerous_tag:
        if tag.lower() in payload.lower() and tag.lower() in response_text.lower():
            # Confirma que não está codificando com &lt:
            if "&lt;" not in response_text[response_text.lower().find(tag.lower())-5 : response_text.lower().find(tag.lower())+10]:
                return True
    return False

def run(client: HTTPClient, endpoint: str, params: dict, method: str = "GET") -> list[dict]:

    """
    Função executa fuzzing de Reflected XSS em cada parâmetro  fornecido.
    """
    
    findings = []
    payloads = carregar_payloads()

    for param_name in params:
        print(f" [XSS] Testando parâmetro: '{param_name}' em {endpoint}")
        for payload in payloads:
            fuzzed_params = params.copy()
            fuzzed_params[param_name] = payload

            if method == "GET":
                response = client.get(endpoint, params=fuzzed_params)
            else:
                response = client.post(endpoint, data=fuzzed_params)
            
            if response is None:
                continue

            if payload_reflected(response.text, payload):
                finding = {
                    "type":       "Reflected XSS",
                    "endpoint":   endpoint,
                    "param":      param_name,
                    "payload":    payload,
                    "method":     method,
                    "status":     response.status_code,
                    "evidence":   response.text[:300],
                    "confidence": "Alta",
                }
                findings.append(finding)
                print(f" [!] XSS REFLETIVO | param='{param_name}' | payload='{payload}'")
                break # Primeiro hit por parâmetro
    
    return findings