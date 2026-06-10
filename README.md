# 🛡️ web-vuln-scanner

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OWASP](https://img.shields.io/badge/OWASP-Top%2010-000000?style=for-the-badge&logo=owasp&logoColor=white)
![Purpose](https://img.shields.io/badge/Purpose-Educational-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> Scanner automatizado de vulnerabilidades web construído do zero em Python, baseado nas técnicas do **OWASP Top 10**.  
> Desenvolvido para fins estritamente educacionais e de portfólio em segurança ofensiva.

---

## ⚠️ Aviso Ético

> **Este projeto foi desenvolvido exclusivamente para fins educacionais.**  
> Utilize-o **somente em ambientes controlados** que você possui permissão explícita para testar, como laboratórios locais (DVWA, WebGoat, HackTheBox, TryHackMe).  
> O uso não autorizado contra sistemas de terceiros é ilegal e antiético.  
> O autor não se responsabiliza por uso indevido desta ferramenta.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Vulnerabilidades Detectadas](#-vulnerabilidades-detectadas)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Ambiente de Testes com DVWA](#-ambiente-de-testes-com-dvwa)
- [Uso](#-uso)
- [Exemplos de Saída](#-exemplos-de-saída)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Funciona Cada Módulo](#-como-funciona-cada-módulo)
- [Tratamento de Falsos Positivos](#-tratamento-de-falsos-positivos)
- [Limitações Conhecidas](#-limitações-conhecidas)
- [Roadmap](#-roadmap)
- [Autor](#-autor)

---

## 🎯 Sobre o Projeto

O **web-vuln-scanner** é um scanner de vulnerabilidades web desenvolvido do zero com o objetivo de demonstrar, de forma prática e educacional, como ferramentas de segurança ofensiva funcionam internamente.

Ao invés de usar scanners prontos como o OWASP ZAP ou o Nikto como caixa-preta, este projeto expõe cada camada da detecção — desde o cliente HTTP até a lógica de análise de resposta — tornando-o ideal para quem quer **entender o mecanismo, não apenas executar o binário**.

**O que este projeto demonstra:**
- Construção de um cliente HTTP com sessão persistente e gestão de cookies
- Fuzzing sistemático de parâmetros GET e POST com wordlists
- Análise de respostas HTTP para identificar assinaturas de vulnerabilidade
- Heurísticas para reduzir falsos positivos
- Geração de relatórios estruturados em JSON

---

## 🔍 Vulnerabilidades Detectadas

| Vulnerabilidade | OWASP Top 10 | Técnica | Confiança Máxima |
|---|---|---|---|
| **SQL Injection** | A03:2021 – Injection | Fuzzing + regex de erros de DB | Alta |
| **Reflected XSS** | A03:2021 – Injection | Reflexão de payload sem encoding | Alta |
| **Directory Traversal** | A01:2021 – Broken Access Control | Assinaturas de arquivos sensíveis | Alta |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│           scanner.py (CLI)          │
│   --url  --cookie  --output         │
└────────────┬────────────────────────┘
             │ orquestra
    ┌────────▼────────┐
    │  core/          │
    │  http_client.py │  ← sessão · GET · POST · headers
    └────────┬────────┘
             │ instancia
    ┌────────▼──────────────────────────────┐
    │            modules/                   │
    │  sqli.py · xss.py · traversal.py      │
    └────────────────────┬──────────────────┘
                         │ retorna findings[]
    ┌────────────────────▼──────────────────┐
    │           utils/reporter.py           │
    │  console colorido · relatório JSON    │
    └───────────────────────────────────────┘
```

---

## 📦 Requisitos

- Python 3.11+
- Docker (para ambiente de testes com DVWA)
- pip

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/SLGusta/web-vuln-scanner.git
cd web-vuln-scanner

# 2. (Recomendado) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# ou
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

**`requirements.txt`:**
```
requests>=2.31.0
colorama>=0.4.6
urllib3>=2.0.0
```

---

## 🐳 Ambiente de Testes com DVWA

> O DVWA (Damn Vulnerable Web Application) é a aplicação recomendada para validar o scanner de forma segura e ética.

```bash
# 1. Suba o container DVWA
docker run -d \
  --name dvwa \
  -p 80:80 \
  vulnerables/web-dvwa

# 2. Acesse no navegador
# http://localhost/setup.php
# → Clique em "Create / Reset Database"

# 3. Faça login
# URL:   http://localhost/login.php
# User:  admin
# Pass:  password

# 4. Configure o nível de segurança
# Acesse: DVWA Security → selecione "Low" → Save

# 5. Obtenha o cookie de sessão
# DevTools (F12) → Application → Cookies → copie PHPSESSID
```

---

## 💻 Uso

### Sintaxe básica

```bash
python scanner.py --url <URL_BASE> --cookie "<COOKIE>" [--output]
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `--url` | ✅ | URL base do alvo (ex: `http://localhost/dvwa`) |
| `--cookie` | ❌ | Cookie de sessão (ex: `PHPSESSID=abc123; security=low`) |
| `--output` | ❌ | Salva relatório em JSON com timestamp |

### Exemplos de uso

```bash
# Varredura simples
python scanner.py --url "http://localhost/dvwa" \
  --cookie "PHPSESSID=abc123xyz; security=low"

# Varredura com relatório JSON
python scanner.py --url "http://localhost/dvwa" \
  --cookie "PHPSESSID=abc123xyz; security=low" \
  --output

# Verificar ajuda
python scanner.py --help
```

---

## 📊 Exemplos de Saída

### Terminal (saída colorida)

```
[*] Alvo: http://localhost/dvwa
[*] Iniciando varredura...

[MODULE] SQL Injection
  [SQLi] Testando parâmetro: 'id' em vulnerabilities/sqli/
    [!] POSSÍVEL SQLi | param='id' | payload=''' | DB=MySQL

[MODULE] Reflected XSS
  [XSS] Testando parâmetro: 'name' em vulnerabilities/xss_r/
    [!] XSS REFLETIDO | param='name' | payload='<script>alert('XSS')</script>'

[MODULE] Directory Traversal
  [Traversal] Testando parâmetro: 'page' em vulnerabilities/fi/
    [!] TRAVERSAL | payload='../../etc/passwd' | assinatura='root:x:0:0'

============================================================
  3 VULNERABILIDADE(S) ENCONTRADA(S)
============================================================

[1] SQL Injection — Confiança: Alta
    Endpoint : vulnerabilities/sqli/
    Parâmetro: id
    Payload  : '
    Método   : GET | Status HTTP: 200
    Motor DB : MySQL
    Evidência:
    You have an error in your SQL syntax; check the manual...

[2] Reflected XSS — Confiança: Alta
    Endpoint : vulnerabilities/xss_r/
    Parâmetro: name
    Payload  : <script>alert('XSS')</script>
    Método   : GET | Status HTTP: 200
    Evidência:
    Hello <script>alert('XSS')</script>

[3] Directory Traversal — Confiança: Alta
    Endpoint : vulnerabilities/fi/
    Parâmetro: page
    Payload  : ../../etc/passwd
    Método   : GET | Status HTTP: 200
    Assinatura: root:x:0:0
    Evidência:
    root:x:0:0:root:/root:/bin/bash daemon:x:1:1:...

[+] Relatório salvo em: report_20250610_143022.json
```

### Relatório JSON (`report_*.json`)

```json
{
  "scanner": "web-vuln-scanner v1.0",
  "target": "http://localhost/dvwa",
  "timestamp": "2025-06-10T14:30:22.841503",
  "total": 3,
  "findings": [
    {
      "type": "SQL Injection",
      "endpoint": "vulnerabilities/sqli/",
      "param": "id",
      "payload": "'",
      "method": "GET",
      "db_engine": "MySQL",
      "status": 200,
      "evidence": "You have an error in your SQL syntax...",
      "confidence": "Alta"
    },
    {
      "type": "Reflected XSS",
      "endpoint": "vulnerabilities/xss_r/",
      "param": "name",
      "payload": "<script>alert('XSS')</script>",
      "method": "GET",
      "status": 200,
      "evidence": "Hello <script>alert('XSS')</script>",
      "confidence": "Alta"
    },
    {
      "type": "Directory Traversal",
      "endpoint": "vulnerabilities/fi/",
      "param": "page",
      "payload": "../../etc/passwd",
      "method": "GET",
      "status": 200,
      "evidence": "root:x:0:0:root:/root:/bin/bash...",
      "signature": "root:x:0:0",
      "confidence": "Alta"
    }
  ]
}
```

---

## 📁 Estrutura do Projeto

```
web-vuln-scanner/
├── scanner.py              ← ponto de entrada (CLI)
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
├── core/
│   ├── __init__.py
│   └── http_client.py      ← módulo base HTTP reutilizável
├── modules/
│   ├── __init__.py
│   ├── sqli.py             ← SQL Injection fuzzer
│   ├── xss.py              ← Reflected XSS fuzzer
│   └── traversal.py        ← Directory Traversal fuzzer
├── utils/
│   ├── __init__.py
│   └── reporter.py         ← saída colorida + JSON
└── payloads/
    ├── sqli.txt            ← wordlist SQL Injection
    ├── xss.txt             ← wordlist XSS
    └── traversal.txt       ← wordlist path traversal
```

---

## ⚙️ Como Funciona Cada Módulo

### `core/http_client.py`
Núcleo do scanner. Mantém uma sessão `requests.Session()` persistente que reutiliza cookies entre requisições — essencial para escanear aplicações autenticadas. Centraliza timeout, headers e supressão de warnings SSL para ambientes de teste.

### `modules/sqli.py`
Injeta cada payload da wordlist em cada parâmetro informado. Analisa a resposta com expressões regulares buscando mensagens de erro características de cada motor de banco de dados (MySQL, PostgreSQL, MSSQL, Oracle, SQLite). Inclui heurística secundária de anomalia de tamanho de resposta para cobrir casos onde o erro não é verboso.

**Por que as aspas funcionam?** A aspa simples `'` quebra a query SQL ao inserir um caractere inesperado fora das aspas da string esperada pelo desenvolvedor. Se a aplicação não tratar o erro, expõe a mensagem interna do banco.

### `modules/xss.py`
Reflete cada payload nos parâmetros e verifica se ele retorna na resposta **sem encoding HTML**. A presença de `&lt;` em vez de `<` indica sanitização correta — a aplicação não é vulnerável. A presença do `<script>` literal indica que o browser executaria o código.

### `modules/traversal.py`
Testa sequências `../` e variações URL-encoded nos parâmetros de caminho. Compara a resposta com uma baseline (resposta normal do endpoint) e busca assinaturas de arquivos sensíveis como `root:x:0:0` (`/etc/passwd`) e `[boot loader]` (`win.ini`).

---

## 🔧 Tratamento de Falsos Positivos

| Módulo | Causa | Mitigação |
|---|---|---|
| SQLi | Aplicação retorna "error" em validações de formulário | Regex específico por motor de DB, não busca genérica |
| SQLi | Mudança de tamanho sem erro real | Confiança `Média` — revisar manualmente |
| XSS | Payload refletido com `&lt;script&gt;` (encoding correto) | Verificação explícita de ausência de HTML encoding |
| Traversal | Resposta diferente sem conteúdo sensível | Confiança `Baixa` — nunca reportado como confirmado |

**Regra geral:** Um finding `Alta confiança` exige evidência técnica direta. Tudo que é suposição entra como `Média` ou `Baixa` para revisão manual.

---

## ⚠️ Limitações Conhecidas

- **Não detecta SQLi cega por tempo** (Blind Time-Based) — requer verificação de `response.elapsed`
- **Não suporta autenticação Bearer Token** — apenas cookies de sessão
- **Single-threaded** — sem paralelismo entre módulos ou parâmetros
- **Não rastreia links** — endpoints precisam ser fornecidos manualmente
- **Sem suporte a JavaScript** — não detecta XSS DOM-based
- **Payloads fixos** — wordlists não são geradas dinamicamente por contexto

---