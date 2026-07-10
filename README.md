<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0f0f,50:16161f,100:1a1a2e&height=140&section=header"/>

<a href="https://github.com/ashfromsky">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=2800&pause=900&color=39FF14&center=true&vCenter=true&width=560&lines=tymofii%40kyiv%3A~%24+whoami;Tymofii+Shchur+%E2%80%94+Software+Engineer;tymofii%40kyiv%3A~%24+cat+focus.txt;Systems+%C2%B7+LLM+Infra+%C2%B7+Microservices;tymofii%40kyiv%3A~%24+_" alt="Typing SVG" />
</a>

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/tymofii-shchur)
[![Email](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:tymofiischur@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ashfromsky)

</div>

<br/>

```
┌──●──●──●───────────────────────────────────────────────────────┐
│  tymofii@kyiv: ~/about                                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  $ cat about.md                                                │
│                                                                │
│  Backend engineer focused on system architecture, API          │
│  design, and CS fundamentals. I build the internals I          │
│  actually want to understand — write-ahead logs, custom        │
│  indexing, concurrency models, LLM pipelines — from            │
│  scratch, at least once, before trusting a library to          │
│  do it for me.                                                 │
│                                                                │
│  Currently technical lead on Smarket, a microservices          │
│  grocery price-comparison platform in production on            │
│  Hetzner.                                                      │
│                                                                │
│  $ █                                                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

<br/>

```
┌──●──●──●───────────────────────────────────────────────────────┐
│  tymofii@kyiv: ~/projects                                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  $ ls -la ./projects                                           │
│                                                                │
│  drwxr-xr-x  smarket/        [technical lead]                  │
│  drwxr-xr-x  acquiremock/    81 stars                          │
│  drwxr-xr-x  yaradb/         34 stars                          │
│  drwxr-xr-x  helix/          25 stars                          │
│  drwxr-xr-x  sentinel-cli/   AMD Dev Hackathon                 │
│  drwxr-xr-x  gitra/          3 stars                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**[Smarket](https://github.com/ashfromsky)** — microservices grocery price-comparison platform `[technical lead]`
Production deployment on Hetzner. Auth, cart, `products_etl`, gateway, and a `zephyros_agent`
AI chat service. Google OAuth2, Redis, three-tier LLM routing (Gemini → Groq → Cerebras).
`Python` `Go` `FastAPI` `PostgreSQL` `Redis` `Docker` `Microservices`

**[AcquireMock](https://github.com/ashfromsky/acquiremock)** — financial payment gateway simulator `★ 81`
Full transaction lifecycle (Invoice → OTP → Webhook) with idempotency keys, HMAC-SHA256 signed
webhooks, exponential backoff retries, bcrypt card storage mirroring PCI-DSS.
`Python` `FastAPI` `SQLModel` `PostgreSQL` `Cryptography`

**[YaraDB](https://github.com/ashfromsky/yaradb)** — custom in-memory database engine `★ 34`
Built from scratch to study DBMS internals: Write-Ahead Logging for crash recovery, dual
indexing with Hash Index O(1) exact lookups and B-Tree O(log n) range queries.
`Python` `WAL` `B-Tree` `Data Structures`

**[Helix](https://github.com/ashfromsky/helix)** — AI-powered API mocking platform `★ 25`
Zero-config mock server guaranteeing JSON-schema-compliant responses via pluggable LLM
providers (Groq, DeepSeek, Ollama), Redis semantic caching, chaos-engineering module.
`Python` `FastAPI` `Redis` `LLMs`

**[Sentinel CLI](https://github.com/ashfromsky/sentinel-cli)** — multi-agent code analysis engine `AMD Developer Hackathon`
Async Scatter-Process-Gather pipeline routing analysis tasks dynamically across models,
optimized for AMD ROCm local inference.
`Python` `AsyncIO` `AMD ROCm` `Ollama`

**[Gitra](https://github.com/ashfromsky/gitra)** — local AI code explorer `★ 3`
RAG-powered natural-language Q&A over any public Git repository via the Gemini API.
`Python` `RAG` `Gemini API` `Vector Search`

<br/>

```
┌──●──●──●───────────────────────────────────────────────────────┐
│  tymofii@kyiv: ~/stack                                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  $ cat stack.yaml                                              │
│                                                                │
│  languages:   Python (Adv) · C#/.NET · Go · C++ · TS           │
│  backend:     FastAPI · Django (DRF) · ASP.NET Core · Async    │
│  ai_llm:      OpenAI · Anthropic · OpenRouter · RAG · YOLOv8   │
│  databases:   PostgreSQL · MongoDB · Redis · MySQL · SQLite    │
│  orm:         SQLAlchemy · SQLModel · EF Core · Django ORM     │
│  devops:      Docker · GH Actions · Linux · Azure · Hetzner    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

<br/>

```
┌──●──●──●───────────────────────────────────────────────────────┐
│  tymofii@kyiv: ~                                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  $ ./run.sh --status                                           │
│                                                                │
│  [ OK ]  shipping Smarket to production                        │
│  [ OK ]  preparing academic defense                            │
│  [ .. ]  self-hosted PostgreSQL migration                      │
│  [ .. ]  Fractalyth — music production, djent/thall            │
│                                                                │
│  process exited with code 0                                    │
│  $ █                                                           │
└────────────────────────────────────────────────────────────────┘
```

<div align="center">
<br/>

![Visitors](https://komarev.com/ghpvc/?username=ashfromsky&color=39FF14&style=for-the-badge&label=PROFILE+VIEWS)

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,50:16161f,100:0f0f0f&height=100&section=footer"/>

</div>
