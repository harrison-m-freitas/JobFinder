# Modelo de Dados (PostgreSQL)

```mermaid
erDiagram
  COMPANIES ||--o{ JOBS : has
  JOBS ||--o{ JOB_SKILLS : tags
  SKILLS ||--o{ JOB_SKILLS : defines
  JOBS ||--o{ JOB_BENEFITS : offers

  COMPANIES {
    uuid id PK
    string name UK
    string website
    string linkedin_url
    string country
    string city
    datetime created_at
    datetime updated_at
  }

  JOBS {
    uuid id PK
    string source
    string external_id
    string source_url
    string title
    string description_html
    string description_text
    uuid company_id FK
    string location
    boolean remote
    string employment_type
    string seniority
    string currency
    decimal salary_min
    decimal salary_max
    json tags
    string language
    datetime posted_at
    datetime scraped_at
    %% Índices: (posted_at), (scraped_at)
    %% UNIQUE composto: (source, external_id)
    %% FK company_id → COMPANIES.id (ON DELETE SET NULL)
  }

  SKILLS {
    uuid id PK
    string name UK
    string category
    datetime created_at
  }

  JOB_SKILLS {
    uuid job_id FK
    uuid skill_id FK
    int weight
  }

  JOB_BENEFITS {
    uuid id PK
    uuid job_id FK
    string name
    %% UNIQUE (job_id, name)
    %% FK job_id → JOBS.id (ON DELETE CASCADE)
  }

  SCRAPING_LOGS {
    uuid id PK
    string source
    string level
    string message
    string url
    int status_code
    string error_type
    json extra
    datetime created_at
    %% Índice: (created_at)
  }

```

## Tabelas

### companies

* `id (uuid, pk)` — gerado via `gen_random_uuid()`
* `name (str, unique, not null)`
* `website (str?)`, `linkedin_url (str?)`, `country (str?)`, `city (str?)`
* `created_at`, `updated_at` (timestamptz)

### jobs

* `id (uuid, pk)`
* `external_id (str?)` + `source (str, not null)` **UNIQUE (source, external_id)**
* `source_url (str, not null)`
* `title (str, not null)`, `description_html (text?)`, `description_text (text?)`
* `company_id (uuid?)` FK→companies (on delete set null)
* `location (str?)`, `remote (bool)`, `employment_type (str?)`, `seniority (str?)`
* `currency (char(3)?)`, `salary_min/max (numeric?)`
* `tags (jsonb?)`, `language (char(5)?)`
* `posted_at (timestamptz?)`, `scraped_at (timestamptz not null)`
* Índices: `(posted_at)`, `(scraped_at)`

### skills

* `id (uuid, pk)`, `name (str unique, not null)`, `category (str?)`, `created_at (timestamptz)`

### job_skills

* `job_id (uuid, pk, fk)`, `skill_id (uuid, pk, fk)`, `weight (int?)`

### job_benefits

* `id (uuid, pk)`, `job_id (uuid fk, on delete cascade)`, `name (str, not null)`
* UNIQUE `(job_id, name)`

### scraping_logs

* `id (uuid, pk)`, `source (str)`, `level (str)`, `message (text)`
* `url (str?)`, `status_code (int?)`, `error_type (str?)`, `extra (jsonb?)`
* `created_at (timestamptz, indexed)`

## Padrões de Qualidade

* **Freshness**: `scraped_at` obrigatório.
* **Moedas**: ISO 4217 (3 letras).
* **Idioma**: ISO 639-1 (`pt`, `en`, ...).
