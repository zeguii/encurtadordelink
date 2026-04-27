# 🔗 Encurtador de URL Pro (API)

Uma API RESTful de alta performance para encurtamento de URLs, desenvolvida com **FastAPI** e **PostgreSQL** (via Supabase). Este projeto foi construído com foco em segurança, velocidade e rastreamento de dados.

## 🚀 Funcionalidades

* **Encurtamento Inteligente:** Geração de códigos curtos e únicos para qualquer URL.
* **Redirecionamento Rápido:** Encaminhamento direto para o site original (`HTTP 307/302`).
* **Expiração de Links (Escassez):** Suporte nativo a datas de validade. Links expirados retornam erro `410 Gone` automaticamente.
* **Rate Limiting (Segurança):** API blindada contra bots e abusos com limite de 5 requisições por minuto por IP.
* **Analytics Integrado:** Rastreamento em tempo real do número de cliques status do link e data de criação.

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI:** Framework web principal (rápido e com documentação automática).
* **SQLAlchemy:** ORM para manipulação do banco de dados (Versão blindada 1.4).
* **Supabase (PostgreSQL):** Banco de dados em nuvem utilizando *Connection Pooler (IPv4)*.
* **SlowAPI:** Gerenciamento de limite de requisições (Rate Limit).
* **Uvicorn:** Servidor ASGI para rodar a aplicação.

## ⚙️ Como rodar o projeto localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/zeguii/encurtadordelink.git](https://github.com/zeguii/encurtadordelink.git)
   cd encurtadordelink
