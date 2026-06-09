import requests # Utilizada para fazer requisições HTTP
import urllib3  # Complementa o requests, com funcionalidade de baixo nivel para conexões HTTP

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Desabilitar Avisos SSL 

class HTTPClient:

    """
    Classe HTTP Client reutilizavel para:
    reutilizar conexões
    centralizar headers ( Definir e gerenciar os cabeçalhos HTTP)
    centralizar timeout ( Definir e gerenciar o tempo limite de Conexão e Resposta)
    tratar erros
    """

    def __init__(self, base_url, timeout: int = 10, headers: dict = None):

        self.base_url = base_url.rstrip("/") #rstrip("/") Remove barras do final
        self.timeout = timeout
        self.session = requests.Session() 
        """
        requests.Session() Cria uma sessão persistente, a conexão pode ser reutilizada
        Garantindo: Mais rapidez; Menos consumo de recursos; Mantém os cookies
        """
        self.session.verify = False # Ignora validação SSL (Apenas para ambientes de teste locais)

        default_headers = {
            "User-Agent": "WebVulnScanner/1.0 ( Educacional )", # User-Agent Identifica o cliente
            "Accept": "*/*" # Aceita qualquer tipo de resposta
        }

        if headers:
            default_headers.update(headers) # Permite sobrescrever ou adicionar headers
        self.session.headers.update(default_headers) # Todos as requests usarão esses cabeçalhos

    def get(self, path: str = "", params: dict = None) -> requests.Response | None:
        
        """
        Realiza a requisição GET
        """

        url = (
            f"{self.base_url}/{path.lstrip('/')}"
            if path
            else self.base_url
        )

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return response
        except requests.exceptions.ConnectionError:
            print(f"[ERRO] Não foi possível conectar a {url}") # Tratando erro de conexão
        except requests.exceptions.Timeout:
            print(f"[ERRO] Timeout ao acessar {url}")
        return None
    
    def post(self, path: str = "", data: dict = None) -> requests.Response | None:

        """
        Realiza requisição POST com dados de formulario.
        """

        url = (
            f"{self.base_url}/{path.lstrip('/')}"
            if path 
            else self.base_url
        )

        try:
            response = self.session.post(url, data=data, timeout=self.timeout)
            return response
        except requests.exceptions.ConnectionError:
            print(f"[ERRO] Não foi possível conectar a {url}")
        except requests.exceptions.Timeout:
            print(f"[ERRO] Timeout ao acessar {url}")
        return None