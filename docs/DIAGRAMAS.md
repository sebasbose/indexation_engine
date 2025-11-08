# Diagramas del Sistema

## Arquitectura General

```
┌──────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                              │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP (Browser)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            WEB FRONTEND (Next.js)                            │
│                  Puerto: 3000                                │
│  - Interfaz de búsqueda                                      │
│  - Visualización de resultados                               │
│  - Estadísticas del sistema                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (JSON)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          API GATEWAY (Node.js + Express)                     │
│                  Puerto: 3001                                │
│  Endpoints:                                                  │
│  - GET /api/search?q=...  (Búsqueda distribuida)            │
│  - GET /api/stats         (Estadísticas)                     │
│  - GET /api/health        (Health check)                     │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │                  │                  │
        │ SQL              │ SQL              │ NoSQL
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│    MySQL      │  │  PostgreSQL   │  │   MongoDB     │
│  (Metadata)   │  │    (Index)    │  │  (Content)    │
│  Puerto: 3306 │  │  Puerto: 5432 │  │ Puerto: 27017 │
└───────────────┘  └───────────────┘  └───────────────┘
        ▲                  ▲                  ▲
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           │ Write Operations
                           │
                    ┌──────────────┐
                    │    INGEST    │
                    │  (Consumer)  │
                    │   Python     │
                    └──────┬───────┘
                           │
                           │ Kafka Messages
                           ▼
                    ┌──────────────┐
                    │    KAFKA     │
                    │  Message     │
                    │   Broker     │
                    │ Puerto: 9092 │
                    └──────┬───────┘
                           │
                           │ Publish Messages
                           ▲
                    ┌──────────────┐
                    │   CRAWLER    │
                    │   (Scrapy)   │
                    │   Python     │
                    └──────┬───────┘
                           │
                           │ HTTP Requests
                           ▼
                    ┌──────────────┐
                    │   Internet   │
                    │  Web Pages   │
                    └──────────────┘
```

---

## Flujo de Indexación

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: CRAWLING                                             │
└─────────────────────────────────────────────────────────────┘

1. Crawler lee URLs semilla
   └─> https://en.wikipedia.org/wiki/Database
   └─> https://www.python.org/
   └─> ...

2. Crawler solicita página
   └─> HTTP GET request
   └─> Respeta robots.txt
   └─> Aplica delay (0.5s)

3. Crawler extrae datos
   ├─> Title: "Database - Wikipedia"
   ├─> Description: "A database is an organized..."
   ├─> Keywords: "database, data, management"
   └─> Content: "A database is an organized collection..."

4. Crawler crea mensaje
   └─> JSON con todos los campos
   └─> document_id = md5(url)

5. Crawler publica a Kafka
   └─> Topic: pages.raw
   └─> Key: document_id
   └─> Value: JSON message

┌─────────────────────────────────────────────────────────────┐
│ FASE 2: PROCESAMIENTO                                        │
└─────────────────────────────────────────────────────────────┘

6. Ingest consume mensaje de Kafka
   └─> Group: ingest-consumer-group
   └─> Lee mensaje JSON

7. Ingest tokeniza contenido
   ├─> Lowercase: "database is an organized..."
   ├─> Remove punctuation
   ├─> Split: ["database", "organized", "collection", ...]
   └─> Count frequencies: {database: 15, organized: 5, ...}

8. Ingest almacena en MySQL
   └─> INSERT INTO documents (document_id, url, title, description, ...)

9. Ingest almacena en MongoDB
   └─> db.documents.insertOne({document_id, content, ...})

10. Ingest almacena en PostgreSQL
    └─> Para cada token:
        INSERT INTO inverted_index (token, document_id, frequency)

┌─────────────────────────────────────────────────────────────┐
│ FASE 3: DISPONIBLE PARA BÚSQUEDA                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de Búsqueda

```
┌─────────────────────────────────────────────────────────────┐
│ BÚSQUEDA: "python database"                                  │
└─────────────────────────────────────────────────────────────┘

1. Usuario ingresa query en UI
   └─> Input: "python database"

2. Frontend envía request a API
   └─> GET /api/search?q=python%20database

3. API tokeniza query
   └─> ["python", "database"]

4. API consulta PostgreSQL (ÍNDICE)
   ┌──────────────────────────────────────────────┐
   │ SELECT document_id, SUM(frequency) as score  │
   │ FROM inverted_index                          │
   │ WHERE token IN ('python', 'database')        │
   │ GROUP BY document_id                         │
   │ ORDER BY score DESC                          │
   │ LIMIT 10                                     │
   └──────────────────────────────────────────────┘
   
   Resultado:
   ┌────────────┬───────┐
   │ document_id│ score │
   ├────────────┼───────┤
   │ abc123     │  42   │
   │ def456     │  35   │
   │ ghi789     │  28   │
   └────────────┴───────┘

5. API consulta MySQL (METADATA)
   ┌──────────────────────────────────────────────┐
   │ SELECT url, title, description               │
   │ FROM documents                               │
   │ WHERE document_id IN ('abc123', 'def456'...) │
   └──────────────────────────────────────────────┘
   
   Resultado:
   - abc123: "Python Official Site", "www.python.org"
   - def456: "Database Systems", "wikipedia.org/..."

6. API consulta MongoDB (CONTENIDO)
   ┌──────────────────────────────────────────────┐
   │ db.documents.find({                          │
   │   document_id: {$in: ['abc123', 'def456']}   │
   │ })                                           │
   └──────────────────────────────────────────────┘
   
   Resultado:
   - abc123: content: "Python is a high-level..."
   - def456: content: "A database is a collection..."

7. API agrega resultados
   ┌────────────────────────────────────────────┐
   │ {                                          │
   │   document_id: "abc123",                   │
   │   score: 42,                               │
   │   title: "Python Official Site",           │
   │   url: "www.python.org",                   │
   │   description: "...",                      │
   │   snippet: "Python is a high-level..."     │
   │ }                                          │
   └────────────────────────────────────────────┘

8. API retorna JSON a frontend

9. Frontend renderiza resultados
   ┌────────────────────────────────────────────┐
   │ ■ Python Official Site                     │
   │ www.python.org                             │
   │ Python is a high-level programming         │
   │ language...                                │
   │ Score: 42 | Source: python.org             │
   └────────────────────────────────────────────┘
```

---

## Modelo de Datos

### MySQL - Tabla `documents`

```
┌────┬─────────────┬──────────────────┬─────────────────┬───────────────┬──────────┬──────────────────┬────────────┐
│ id │ document_id │       url        │      title      │  description  │ keywords │ crawl_timestamp  │   source   │
├────┼─────────────┼──────────────────┼─────────────────┼───────────────┼──────────┼──────────────────┼────────────┤
│  1 │ abc123...   │ python.org       │ Python Home     │ Official site │ python   │ 2025-11-07 10:30 │ python.org │
│  2 │ def456...   │ wikipedia.org/db │ Database Wiki   │ Database info │ database │ 2025-11-07 10:32 │ wikipedia  │
│  3 │ ghi789...   │ nodejs.org       │ Node.js Home    │ JS runtime    │ nodejs   │ 2025-11-07 10:35 │ nodejs.org │
└────┴─────────────┴──────────────────┴─────────────────┴───────────────┴──────────┴──────────────────┴────────────┘
```

### PostgreSQL - Tabla `inverted_index`

```
┌────┬──────────┬─────────────┬───────────┬───────────┬─────────────────────┐
│ id │  token   │ document_id │ frequency │ positions │    created_at       │
├────┼──────────┼─────────────┼───────────┼───────────┼─────────────────────┤
│  1 │ python   │ abc123...   │    25     │ [1,5,12]  │ 2025-11-07 10:30:00 │
│  2 │ database │ abc123...   │     3     │ [45,67]   │ 2025-11-07 10:30:00 │
│  3 │ database │ def456...   │    42     │ [1,2,3]   │ 2025-11-07 10:32:00 │
│  4 │ python   │ ghi789...   │     8     │ [23,45]   │ 2025-11-07 10:35:00 │
│  5 │ language │ abc123...   │    15     │ [8,9,10]  │ 2025-11-07 10:30:00 │
└────┴──────────┴─────────────┴───────────┴───────────┴─────────────────────┘

Índices:
- idx_token: Para búsqueda rápida por token
- idx_document_id: Para búsqueda por documento
- UNIQUE(token, document_id): Evita duplicados
```

### MongoDB - Colección `documents`

```javascript
{
  _id: ObjectId("..."),
  document_id: "abc123...",
  url: "https://www.python.org/",
  content: "Python is a high-level, interpreted, interactive and object-oriented...",
  title: "Welcome to Python.org",
  crawl_timestamp: ISODate("2025-11-07T10:30:00Z")
}

{
  _id: ObjectId("..."),
  document_id: "def456...",
  url: "https://en.wikipedia.org/wiki/Database",
  content: "A database is an organized collection of structured information...",
  title: "Database - Wikipedia",
  crawl_timestamp: ISODate("2025-11-07T10:32:00Z")
}
```

---

## Tokenización

```
Input: "Python is a high-level programming language!"

┌────────────────────────────────────┐
│ PASO 1: Lowercase                  │
└────────────────────────────────────┘
"python is a high-level programming language!"

┌────────────────────────────────────┐
│ PASO 2: Remove Punctuation         │
└────────────────────────────────────┘
"python is a high level programming language"

┌────────────────────────────────────┐
│ PASO 3: Split by Whitespace        │
└────────────────────────────────────┘
["python", "is", "a", "high", "level", "programming", "language"]

┌────────────────────────────────────┐
│ PASO 4: Filter Short Tokens (< 3)  │
└────────────────────────────────────┘
["python", "high", "level", "programming", "language"]

┌────────────────────────────────────┐
│ PASO 5: Count Frequencies          │
└────────────────────────────────────┘
{
  "python": 1,
  "high": 1,
  "level": 1,
  "programming": 1,
  "language": 1
}
```

---

## Scoring de Búsqueda

```
Query: "python database"
Tokens: ["python", "database"]

Documentos en índice:

Document abc123:
  - token "python": frequency = 25
  - token "database": frequency = 3
  → Score = 25 + 3 = 28

Document def456:
  - token "python": frequency = 0 (no aparece)
  - token "database": frequency = 42
  → Score = 0 + 42 = 42

Document ghi789:
  - token "python": frequency = 8
  - token "database": frequency = 0 (no aparece)
  → Score = 8 + 0 = 8

Ranking Final (DESC):
1. def456 (score: 42)
2. abc123 (score: 28)
3. ghi789 (score: 8)
```

---

## Tolerancia a Fallos

```
Escenario: MySQL caído

┌─────────────────────────────────────┐
│ Usuario busca "python"              │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ API Gateway                          │
└─┬─────────┬─────────────┬───────────┘
  │         │             │
  ▼         ▼             ▼
┌────┐  ┌────────┐  ┌─────────┐
│ ✗  │  │   ✓    │  │    ✓    │
│MySQL│  │Postgres│  │ MongoDB │
└────┘  └────────┘  └─────────┘
(CAÍDO)   (OK)        (OK)

API Gateway detecta fallo de MySQL:
- Continúa con PostgreSQL (índice)
- Continúa con MongoDB (contenido)
- Retorna resultados parciales:
  {
    results: [...],
    partial: true,
    message: "MySQL unavailable, metadata limited"
  }

Usuario recibe:
- Resultados (aunque sin metadata completa)
- Advertencia de servicio parcial
- Sistema sigue funcionando
```

---

## Escalabilidad Horizontal

```
┌──────────────────────────────────────────────────────────┐
│ ESCALAMIENTO DE CRAWLER                                  │
└──────────────────────────────────────────────────────────┘

  Crawler 1          Crawler 2          Crawler 3
  (URLs 0-166)      (URLs 167-333)     (URLs 334-500)
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                    ┌───────────┐
                    │   Kafka   │
                    └───────────┘

┌──────────────────────────────────────────────────────────┐
│ ESCALAMIENTO DE INGEST                                   │
└──────────────────────────────────────────────────────────┘

                    ┌───────────┐
                    │   Kafka   │
                    │ (3 partitions)
                    └─────┬─────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      Ingest 1       Ingest 2      Ingest 3
    (partition 0)  (partition 1)  (partition 2)
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                   [Databases]

┌──────────────────────────────────────────────────────────┐
│ ESCALAMIENTO DE API                                      │
└──────────────────────────────────────────────────────────┘

   [Load Balancer]
          │
    ┌─────┼─────┬─────┐
    ▼     ▼     ▼     ▼
   API1  API2  API3  API4
    │     │     │     │
    └─────┴─────┴─────┘
          │
    [Databases]
```

---

## Diagrama de Despliegue (Docker)

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Host                             │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Network: search-network (bridge)           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Zookeeper │  │  Kafka   │  │  Crawler │             │
│  │:2181     │←─│:9092     │←─│  (Scrapy)│             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                     ↓                                    │
│                ┌──────────┐                             │
│                │  Ingest  │                             │
│                │(Consumer)│                             │
│                └────┬─────┘                             │
│                     ↓                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  MySQL   │  │Postgres  │  │ MongoDB  │             │
│  │  :3306   │  │  :5432   │  │  :27017  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                     │
│       └─────────────┼─────────────┘                     │
│                     ↓                                    │
│                ┌──────────┐                             │
│                │   API    │                             │
│                │  :3001   │                             │
│                └────┬─────┘                             │
│                     ↓                                    │
│                ┌──────────┐                             │
│                │   Web    │                             │
│                │  :3000   │                             │
│                └──────────┘                             │
│                     ↓                                    │
└─────────────────────┼──────────────────────────────────┘
                      ↓
               [Usuario: Browser]
```

---

_Diagramas ASCII para documentación del proyecto_
_Última actualización: 7 de noviembre, 2025_
