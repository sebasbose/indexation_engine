# Arquitectura del Sistema de Búsqueda Distribuido

## Diagrama de Componentes

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────┐
│   Web (Next.js) │
│   Puerto: 3000  │
└────────┬────────┘
         │ REST API
         ▼
┌──────────────────┐      ┌──────────────┐
│  API Gateway     │─────▶│    MySQL     │
│  (Node.js)       │      │  (Metadata)  │
│  Puerto: 3001    │      └──────────────┘
└────────┬─────────┘
         │              ┌──────────────┐
         ├─────────────▶│  PostgreSQL  │
         │              │   (Index)    │
         │              └──────────────┘
         │
         │              ┌──────────────┐
         └─────────────▶│   MongoDB    │
                        │  (Content)   │
                        └──────────────┘


┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Crawler    │─────▶│    Kafka     │─────▶│    Ingest    │
│  (Scrapy)    │      │  (Message    │      │  (Consumer)  │
└──────────────┘      │   Queue)     │      └──────┬───────┘
                      └──────────────┘             │
                                                   │
                           ┌───────────────────────┼───────────────────────┐
                           ▼                       ▼                       ▼
                      ┌─────────┐           ┌──────────┐           ┌──────────┐
                      │  MySQL  │           │ Postgres │           │ MongoDB  │
                      └─────────┘           └──────────┘           └──────────┘
```

## Flujo de Datos

### 1. Proceso de Crawling e Indexación

1. **Crawler** (Scrapy):
   - Visita URLs de la lista de semillas
   - Extrae: título, descripción, keywords, contenido
   - Envía mensaje a Kafka (topic: `pages.raw`)

2. **Kafka**:
   - Recibe mensajes del crawler
   - Almacena en cola para procesamiento asíncrono
   - Garantiza entrega de mensajes

3. **Ingest Service**:
   - Consume mensajes de Kafka
   - Procesa y tokeniza contenido
   - Almacena en 3 bases de datos:
     - **MySQL**: `document_id, url, title, description, keywords`
     - **MongoDB**: `document_id, content, raw_html`
     - **PostgreSQL**: `token, document_id, frequency`

### 2. Proceso de Búsqueda

1. **Usuario** ingresa query en interfaz web
2. **Web Frontend** envía request a API: `GET /api/search?q=query`
3. **API Gateway**:
   - Tokeniza la query
   - Consulta **PostgreSQL** para encontrar documentos con tokens coincidentes
   - Obtiene metadata de **MySQL**
   - Obtiene snippets de **MongoDB**
   - Agrega y ordena resultados por score
   - Retorna JSON con resultados combinados
4. **Web Frontend** muestra resultados al usuario

## Modelo de Datos

### MySQL (Metadata)

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    keywords TEXT,
    crawl_timestamp TIMESTAMP,
    source VARCHAR(255),
    INDEX idx_document_id (document_id)
);
```

### PostgreSQL (Inverted Index)

```sql
CREATE TABLE inverted_index (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    frequency INT DEFAULT 1,
    positions JSONB,
    created_at TIMESTAMP,
    UNIQUE(token, document_id)
);
```

### MongoDB (Content)

```javascript
{
  document_id: "abc123",
  url: "https://example.com",
  content: "Full page content...",
  title: "Page Title",
  crawl_timestamp: ISODate("2025-11-07T...")
}
```

## Estrategia de Distribución

### Fragmentación (Sharding)

- **Criterio**: Hash del `document_id` o `url`
- **Fórmula**: `shard_id = hash(document_id) % N_SHARDS`
- **Ventaja**: Distribución uniforme de datos

### Replicación

- **MySQL**: Primary-Replica (Master-Slave)
- **PostgreSQL**: Streaming Replication
- **MongoDB**: Replica Set (1 Primary + 2 Secundarios)

### Tolerancia a Fallos

- API verifica disponibilidad de cada nodo
- Si un nodo falla, continúa con resultados parciales
- Marca origen de datos en respuesta

## Escalabilidad

### Horizontal

1. **Crawler**: Múltiples instancias consumiendo de lista de URLs
2. **Ingest**: Consumer group de Kafka permite paralelización
3. **API**: Load balancer con múltiples instancias
4. **Web**: Múltiples instancias detrás de nginx

### Vertical

1. **Bases de datos**: Incrementar recursos (CPU, RAM, Disco)
2. **Kafka**: Más particiones por topic
3. **Índices**: Optimizar consultas con índices adicionales

## Métricas de Performance

### Objetivos

- **Latencia de búsqueda**: < 200ms (p95)
- **Throughput de crawling**: > 100 páginas/min
- **Throughput de indexación**: > 50 documentos/seg
- **Disponibilidad**: > 99.5%

### Monitoreo

- Logs centralizados (stdout capturados por Docker)
- Health checks en `/api/health`
- Estadísticas en `/api/stats`

## Consideraciones de Seguridad

- Validación de entrada en búsquedas (prevenir injection)
- Rate limiting en API
- Autenticación básica (futuro)
- Robots.txt compliance en crawler
