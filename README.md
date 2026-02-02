# LicitaScan

[![CI](https://github.com/bruno-portfolio/LicitaScan/actions/workflows/ci.yml/badge.svg)](https://github.com/bruno-portfolio/LicitaScan/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Scanner de licitações públicas com interface web. Busca oportunidades abertas no **Portal Nacional de Contratações Públicas (PNCP)** com filtros inteligentes por área de atuação.

<img width="1815" height="918" alt="image" src="https://github.com/user-attachments/assets/0ee18174-1e69-4bd1-b40d-e49576b9eadc" />
<img width="1811" height="937" alt="image" src="https://github.com/user-attachments/assets/86e29173-ef59-46ea-a8bd-8543b8423807" />

## Features

- **Interface Web** — Streamlit com design responsivo
- **Presets por Área** — Agronomia, TI, Engenharia Civil ou personalizado
- **Filtros Avançados** — Estados, modalidades, período, blacklist
- **Apenas Abertas** — Foco em oportunidades reais
- **Export** — Download em Excel e CSV
- **100% Async** — Performance otimizada com httpx

## Quick Start

### Local

```bash
git clone https://github.com/bruno-portfolio/LicitaScan.git
cd LicitaScan

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
streamlit run app.py
```

### Docker

```bash
docker-compose up -d
# http://localhost:8501
```

## Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | Streamlit |
| HTTP Client | httpx (async) |
| Validação | Pydantic |
| Export | pandas + openpyxl |
| Testes | pytest + pytest-asyncio |
| CI/CD | GitHub Actions |
| Deploy | Streamlit Cloud / Docker |

## Estrutura

```
licitascan/
├── app.py                    # Entry point
├── src/
│   ├── config.py             # Settings + presets
│   ├── api/
│   │   └── pncp_client.py    # Cliente async
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── filters/
│   │   └── matcher.py        # Regex matching
│   ├── services/
│   │   └── scanner.py        # Orquestração
│   └── export/
│       └── excel.py          # Export xlsx/csv
└── tests/
```

## Testes

```bash
pytest tests/ -v
```

## Deploy

**Streamlit Cloud:**
1. Fork o repositório
2. Conecte em [share.streamlit.io](https://share.streamlit.io)
3. Selecione `app.py`

## Licença

[MIT](https://github.com/bruno-portfolio/LicitaScan/blob/main/LICENSE) 

---

Dados do [Portal Nacional de Contratações Públicas](https://pncp.gov.br/)
