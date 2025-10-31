# Épica: Sistema de Coleta e Análise de Vagas de Tecnologia

## 📋 Descrição Geral

Desenvolver um sistema automatizado de web scraping para coletar, armazenar e processar ofertas de trabalho na área de tecnologia de múltiplas fontes (job boards, sites de empresas, redes profissionais). O sistema deve consolidar dados de vagas preferencialmente no Brasil e remotas, armazenando informações detalhadas para posterior análise de inteligência de mercado.

## 🎯 Objetivos

- Automatizar a coleta de vagas de tecnologia de múltiplas fontes
- Centralizar informações em banco de dados estruturado
- Coletar dados ricos para análise de mercado e inteligência competitiva
- Possibilitar análises de tendências salariais, skills demandadas, empresas contratantes
- Monitorar oportunidades em tempo real

## 🔍 Escopo

### Áreas de Tecnologia Alvo
- Desenvolvimento de Software (Junior, Mid-level, Senior)
- Cybersecurity / Segurança da Informação
- Pentester / Ethical Hacking
- QA / Quality Assurance
- DevOps / SRE
- Data Science / Machine Learning
- Cloud Computing
- Mobile Development
- Frontend / Backend / Full Stack

### Localização
- **Primário**: Brasil (todas as regiões)
- **Secundário**: Vagas remotas internacionais
- **Idiomas**: Português e Inglês

## 📊 Fontes de Dados (Sources/Providers)

### Job Boards Generalistas
- LinkedIn Jobs
- Indeed Brasil
- Glassdoor
- Catho
- InfoJobs
- Gupy
- Workana
- Trampos.co

### Plataformas Especializadas em Tech
- GeekHunter
- Revelo
- Hired
- Stack Overflow Jobs
- GitHub Jobs
- AngelList (Wellfound)
- Remote.co
- We Work Remotely
- RemoteOK

### Sites de Empresas (Career Pages)
**Big Tech**
- Google Careers
- Amazon Jobs
- Microsoft Careers
- Meta Careers
- Apple Jobs

**Empresas Brasileiras**
- Banco Inter Carreiras
- Mercado Livre Carreiras
- Nubank Careers
- Stone Careers
- iFood Careers
- Loggi Careers
- QuintoAndar Careers
- PicPay Careers
- B2W Digital

**Consultorias / Tech Companies**
- Thoughtworks
- CI&T
- TOTVS
- Stefanini
- Accenture Brasil

## 💾 Modelagem de Dados Sugerida

### Tabela: `jobs`
```
- id (PK, UUID)
- external_id (identificador único da fonte)
- title (título da vaga)
- company_id (FK para companies)
- source (origem da vaga: linkedin, indeed, etc)
- source_url (URL original da vaga)
- description (descrição completa em texto)
- description_html (descrição original em HTML)
- seniority_level (junior, mid, senior, staff, principal)
- employment_type (full-time, part-time, contract, internship)
- location_city
- location_state
- location_country
- is_remote (boolean)
- remote_type (fully_remote, hybrid, on_site)
- salary_min (decimal)
- salary_max (decimal)
- salary_currency
- salary_period (monthly, annual)
- posted_date (data de publicação)
- expires_date (data de expiração)
- applicants_count (número de candidatos)
- status (active, expired, filled, removed)
- scraped_at (timestamp da coleta)
- updated_at (última atualização)
- created_at
```

### Tabela: `companies`
```
- id (PK, UUID)
- name
- normalized_name (nome normalizado para matching)
- website
- industry (setor/indústria)
- size (startup, small, medium, large, enterprise)
- employee_count_min
- employee_count_max
- location_hq (sede principal)
- description
- logo_url
- linkedin_url
- glassdoor_url
- created_at
- updated_at
```

### Tabela: `job_skills`
```
- id (PK)
- job_id (FK)
- skill_id (FK)
- is_required (boolean)
- proficiency_level (basic, intermediate, advanced)
```

### Tabela: `skills`
```
- id (PK)
- name (ex: Python, React, Kubernetes)
- category (language, framework, tool, platform, methodology)
- normalized_name
```

### Tabela: `job_benefits`
```
- id (PK)
- job_id (FK)
- benefit_type (health_insurance, meal_voucher, education, stock_options, etc)
- description
```

### Tabela: `scraping_logs`
```
- id (PK)
- source
- execution_date
- jobs_found
- jobs_inserted
- jobs_updated
- errors_count
- execution_time_seconds
- status (success, partial_failure, failure)
- error_details (JSON)
```

## 🛠️ Stack Tecnológica Recomendada

### Core
- **Linguagem**: Python 3.10+
- **Web Scraping**:
  - Scrapy (framework robusto)
  - BeautifulSoup4 (parsing HTML)
  - Selenium (sites com JavaScript)
  - Playwright (alternativa moderna ao Selenium)
- **HTTP Requests**: httpx, requests
- **APIs**: Quando disponíveis (LinkedIn API, Indeed API)

### Banco de Dados
- **Primário**: PostgreSQL (relacional, JSONB para dados flexíveis)
- **Alternativas**: MySQL, MongoDB (se preferir NoSQL)
- **ORM**: SQLAlchemy ou Django ORM

### Infraestrutura
- **Agendamento**: Apache Airflow, Celery + Redis, ou Cron
- **Containerização**: Docker + Docker Compose
- **Queue**: RabbitMQ ou Redis (para jobs assíncronos)

### Processamento de Dados
- **NLP**: spaCy, NLTK (extração de skills, análise de texto)
- **Matching**: FuzzyWuzzy (deduplicate vagas/empresas)
- **Data Cleaning**: pandas

### Monitoramento
- **Logs**: Python logging + ELK Stack ou Grafana Loki
- **Métricas**: Prometheus + Grafana
- **Alertas**: Email, Slack, Telegram

## 📝 Tarefas e Subtarefas

### 1. Setup e Arquitetura (Story Points: 8)
- [x] 1.1 Definir arquitetura do sistema
- [x] 1.2 Configurar ambiente de desenvolvimento
- [x] 1.3 Setup Docker e Docker Compose
- [x] 1.4 Escolher e configurar banco de dados
- [x] 1.5 Criar estrutura de projeto Python
- [x] 1.6 Configurar sistema de versionamento e CI/CD

### 2. Modelagem e Banco de Dados (Story Points: 13)
- [x] 2.1 Definir modelagem completa de dados
- [x] 2.2 Criar migrations do banco de dados
- [x] 2.3 Implementar models/ORM
- [x] 2.4 Criar índices para otimização
- [x] 2.5 Implementar sistema de backup
- [x] 2.6 Desenvolver scripts de seed/fixtures para testes

### 3. Core do Sistema de Scraping (Story Points: 21)
- [x] 3.1 Criar classe base abstrata para scrapers
- [x] 3.2 Implementar sistema de detecção de robots.txt
- [x] 3.3 Desenvolver rate limiting e delays
- [x] 3.4 Implementar rotação de User-Agents
- [x] 3.5 Sistema de retry com backoff exponencial
- [x] 3.6 Implementar proxy rotation (se necessário)
- [x] 3.7 Sistema de cache para evitar reprocessamento
- [x] 3.8 Deduplicação de vagas

### 4. Scrapers - Job Boards Generalistas (Story Points: 34)
- [ ] 4.1 Scraper: LinkedIn Jobs
- [ ] 4.2 Scraper: Indeed Brasil
- [ ] 4.3 Scraper: Glassdoor
- [ ] 4.4 Scraper: Catho
- [ ] 4.5 Scraper: InfoJobs
- [ ] 4.6 Scraper: Gupy
- [ ] 4.7 Scraper: Trampos.co

### 5. Scrapers - Plataformas Tech (Story Points: 21)
- [ ] 5.1 Scraper: GeekHunter
- [ ] 5.2 Scraper: GitHub Jobs
- [ ] 5.3 Scraper: Stack Overflow Jobs
- [ ] 5.4 Scraper: Remote.co / WeWorkRemotely
- [ ] 5.5 Scraper: AngelList

### 6. Scrapers - Career Pages (Story Points: 34)
- [ ] 6.1 Template genérico para career pages
- [ ] 6.2 Scraper: Google Careers
- [ ] 6.3 Scraper: Amazon Jobs
- [ ] 6.4 Scraper: Mercado Livre
- [ ] 6.5 Scraper: Nubank
- [ ] 6.6 Scraper: Banco Inter
- [ ] 6.7 Scraper: iFood
- [ ] 6.8 Scraper: Stone
- [ ] 6.9 Adicionar mais 5-10 empresas relevantes

### 7. Processamento e Enriquecimento de Dados (Story Points: 21)
- [ ] 7.1 Parser de descrições de vagas (extração de skills)
- [ ] 7.2 Extração de requisitos (anos de experiência, idiomas)
- [ ] 7.3 Normalização de títulos de vagas
- [ ] 7.4 Detecção de nível de senioridade
- [ ] 7.5 Extração e parsing de salários
- [ ] 7.6 Normalização de nomes de empresas
- [ ] 7.7 Geocoding de localizações
- [ ] 7.8 Extração de benefícios

### 8. Sistema de Agendamento (Story Points: 13)
- [ ] 8.1 Configurar Airflow ou alternativa
- [ ] 8.2 Criar DAGs para cada fonte
- [ ] 8.3 Definir frequência de coleta por fonte
- [ ] 8.4 Implementar sistema de priorização
- [ ] 8.5 Configurar alertas de falhas

### 9. API e Interface de Dados (Story Points: 21)
- [ ] 9.1 Criar API REST (FastAPI/Flask)
- [ ] 9.2 Endpoints de consulta de vagas
- [ ] 9.3 Filtros e busca avançada
- [ ] 9.4 Agregações e estatísticas
- [ ] 9.5 Documentação da API (Swagger/OpenAPI)
- [ ] 9.6 Sistema de autenticação

### 10. Monitoramento e Logs (Story Points: 13)
- [ ] 10.1 Implementar logging estruturado
- [ ] 10.2 Dashboard de monitoramento
- [ ] 10.3 Métricas de performance
- [ ] 10.4 Sistema de alertas
- [ ] 10.5 Relatórios automáticos

### 11. Inteligência e Análise (Story Points: 21)
- [ ] 11.1 Análise de tendências salariais
- [ ] 11.2 Skills mais demandadas
- [ ] 11.3 Análise de empregadores
- [ ] 11.4 Análise geográfica
- [ ] 11.5 Previsão de demanda
- [ ] 11.6 Exportação de relatórios

### 12. Qualidade e Testes (Story Points: 13)
- [ ] 12.1 Testes unitários (pytest)
- [ ] 12.2 Testes de integração
- [ ] 12.3 Testes de scrapers com dados mock
- [ ] 12.4 Code coverage > 80%
- [ ] 12.5 Linting e formatação (black, flake8, mypy)

### 13. Documentação (Story Points: 8)
- [ ] 13.1 README detalhado
- [ ] 13.2 Documentação de arquitetura
- [ ] 13.3 Guia de contribuição
- [ ] 13.4 Documentação de cada scraper
- [ ] 13.5 Runbook operacional

## ⚠️ Considerações Técnicas e Legais

### Aspectos Legais
- ✅ Respeitar robots.txt de cada site
- ✅ Implementar rate limiting apropriado
- ✅ Verificar Terms of Service de cada plataforma
- ✅ Considerar uso de APIs oficiais quando disponíveis
- ✅ Não armazenar dados pessoais de candidatos (LGPD compliance)
- ✅ Implementar opt-out se necessário

### Desafios Técnicos
- Sites com proteção anti-bot (Cloudflare, Captcha)
- Mudanças frequentes em estruturas HTML
- Rate limiting agressivo
- Sites que requerem autenticação
- JavaScript-heavy applications (SPAs)
- Dados não estruturados

### Estratégias de Mitigação
- Usar APIs oficiais sempre que possível
- Implementar sistema robusto de error handling
- Cache inteligente para reduzir requests
- Monitoramento contínuo de quebras
- Versionamento de parsers
- Fallback strategies

## 📈 Métricas de Sucesso

- **Cobertura**: Coletar de pelo menos 15 fontes diferentes
- **Volume**: Capturar mínimo de 10.000 vagas ativas
- **Freshness**: Dados atualizados diariamente
- **Qualidade**: Taxa de erro < 5% na extração
- **Performance**: Coleta completa em < 2 horas
- **Uptime**: Sistema rodando 99%+ do tempo

## 🚀 Fases de Entrega

**MVP (Fase 1)** - 2-3 meses
- Setup básico e 5 scrapers principais
- Banco de dados funcional
- Coleta agendada
- API básica

**Fase 2** - 1-2 meses
- 10+ scrapers
- Sistema de enriquecimento
- Dashboard básico
- Análises iniciais

**Fase 3** - 1-2 meses
- Todos os scrapers planejados
- Inteligência avançada
- Machine Learning para classificação
- Sistema completo de monitoramento

## 📚 Recursos e Referências

- [Scrapy Documentation](https://docs.scrapy.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Python](https://selenium-python.readthedocs.io/)
- [Apache Airflow](https://airflow.apache.org/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Estimativa Total**: 241 Story Points (~6-8 meses com 1-2 desenvolvedores)
