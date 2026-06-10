import re # Biblioteca de Expressoes Regulares ( Permite procurar Padroes de Texto )
from core.http_client import HTTPClient # Importando classe HTTPClient

# Padrões de erro de banco de dados por motor SQL
DB_ERROR_PATTERNS = {
    "MySQL": [r"you have an error in your sql syntax", r"warning: mysql", r"mysql_fetch"],
    "PostgreSQL": [r"pg_query\(\)", r"pg_exec\(\)", r"postgresql.*error"],
    "MSSQL": [r"unclosed quotation mark", r"microsoft ole db provider for sql server", r"syntax error"],
    "Oracle": [r"ora-\d{5}", r"oracle error", r"quoted string not properly terminated"],
    "SQLite": [r"sqlite_master", r"sqlite3\.operationalerror"],
    "Genérico": [r"sql syntax", r"sql error", r"database error", r"unrecognized token"],
}

def carregar_payloads(path: str = "payloads/sqli.txt") -> list[str]: # Carrega os payloads que serão usados no fuzzing ( Fuzzing = teste automatizado para identificar falhas)
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()] 

"""
Parâmetro	    Significado
path	        caminho do arquivo
r	            leitura
utf-8	        codificação
"""

def detector_db_error(response_txt: str) -> tuple[bool, str]:

    """
    Analisa o corpo da resposta em busca de mensagens de erro de banco de dados.
    Retorna (encontrou_erro, nome_do_motor).
    """

    text_lower = response_txt.lower() # Converte para minúsculas
    for db_name, patterns in DB_ERROR_PATTERNS.items(): # Percorre todos os bancos
        for pattern in patterns: # Percorre cada regex
            if re.search(pattern, text_lower): # Procura ocorrência
                return True, db_name # Encontrou
    return False, "" # Não encontrou

def run(client: HTTPClient, endpoint: str, params: dict, method: str = "GET") -> list[dict]:

    """
    Executa fuzzing de SQL Injection em cada parâmetro fornecido

    Args:
        client:   instância do HTTPClient
        endpoint: path do endpoint (ex: "vulnerabilities/sqli/")
        params:   dicionário de parâmetros a serem testados (ex: {"id": "1"})
        method:   "GET" ou "POST"

    Returns:
        Lista de achados com detalhes do payload que disparou o erro.
    """

    descobertas = []
    payloads = carregar_payloads()
    if method == "GET":
        original_response = client.get(endpoint, params=params)
    else:
        original_response = client.post(endpoint, data=params)
    original_comprimento = len(original_response.text) if original_response else 0

    for param_name in params:
        print(f" [SQLi] Testando parâmetro: '{param_name}' em {endpoint}")
        for payload in payloads:
            # Substitui apenas o parâmetro alvo, mantém os demais com valores originais
            fuzzed_params = params.copy()
            fuzzed_params[param_name] = payload

            if method == "GET":
                response = client.get(endpoint, params=fuzzed_params)
            else:
                response = client.post(endpoint, data=fuzzed_params)

            if response is None:
                continue
        
            found_error, db_engine = detector_db_error(response.text)

            # Heurística extra: mudança significativa no tamanho da resposta
            length_delta = abs(len(response.text) - original_comprimento)
            length_anomaly = length_delta > 500 and "error" in response.text.lower()

            if found_error or length_anomaly:
                achado = {
                    "type":       "SQL Injection",
                    "endpoint":   endpoint,
                    "param":      param_name,
                    "payload":    payload,
                    "method":     method,
                    "db_engine":  db_engine or "desconhecido",
                    "status":     response.status_code,
                    "evidence":   response.text[:300],  # Primeiros 300 chars como evidência
                    "confidence": "Alta" if found_error else "Média (anomalia de tamanho)",
                }
                descobertas.append(achado)
                print(f"    [!] POSSÍVEL SQLi | param='{param_name}' | payload='{payload}' | DB={db_engine}")
                break  # Para no primeiro hit por parâmetro (evita flood)
    return descobertas