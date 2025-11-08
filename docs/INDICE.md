# 📖 Índice de Documentación

Este documento sirve como guía para navegar toda la documentación del proyecto.

---

## 🚀 Para Empezar (COMIENZA AQUÍ)

1. **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** ⭐ PRIMERO
   - Visión general completa del proyecto
   - Estado actual
   - Cómo empezar en 3 comandos
   - Arquitectura simplificada
   
2. **[QUICKSTART.md](QUICKSTART.md)** ⭐ SEGUNDO
   - Guía paso a paso para levantar el sistema
   - Verificación de componentes
   - Troubleshooting común
   - Comandos esenciales

3. **[CHECKLIST.md](CHECKLIST.md)** ⭐ TERCERO
   - Lista de verificación completa
   - Pasos para validar que todo funciona
   - Checklist de entrega

---

## 📅 Planificación

4. **[PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md)**
   - Roadmap completo de 3 días
   - Tareas día por día
   - Objetivos y métricas
   - Prioridades y riesgos

---

## 🏗️ Arquitectura y Diseño

5. **[arquitectura.md](arquitectura.md)**
   - Arquitectura técnica detallada
   - Componentes del sistema
   - Flujos de datos
   - Modelo de datos
   - Estrategias de distribución

6. **[DIAGRAMAS.md](DIAGRAMAS.md)**
   - Diagramas ASCII del sistema
   - Flujo de indexación
   - Flujo de búsqueda
   - Modelo de datos visualizado
   - Escalabilidad

7. **[NOTAS_IMPLEMENTACION.md](NOTAS_IMPLEMENTACION.md)**
   - Decisiones de diseño
   - Justificación técnica
   - Limitaciones conocidas
   - Mejoras futuras

---

## 🔧 Operaciones y Mantenimiento

8. **[DEBUGGING.md](DEBUGGING.md)**
   - Comandos útiles para cada servicio
   - Consultas a bases de datos
   - Troubleshooting avanzado
   - Scripts de monitoreo
   - Exportación de datos

---

## 📂 Especificación Original

9. **[planteamiento.md](planteamiento.md)**
   - Especificación completa del proyecto
   - Requisitos funcionales
   - Tecnologías requeridas
   - Roadmap sugerido

10. **[Especificación Proyecto Programado BDA.pdf](Especificación%20Proyecto%20Programado%20BDA.pdf)**
    - Documento oficial del curso

---

## 📋 Documentos en la Raíz del Proyecto

### README.md (Raíz)
- Documentación principal del proyecto
- Introducción y características
- Instalación y uso
- Estructura del proyecto
- Mejoras futuras

### .env.example
- Template de variables de entorno
- Configuración de servicios
- Credenciales de ejemplo

### .gitignore
- Archivos a ignorar en Git
- Logs, builds, node_modules, etc.

### Makefile
- Comandos Make para tareas comunes
- `make start`, `make stop`, `make logs`, etc.

### manage.sh
- Script bash para gestión del sistema
- Comandos: start, stop, restart, logs, stats, health, clean, rebuild

---

## 🗂️ Estructura de Directorios

```
indexation_engine/
├── README.md                    # Documentación principal
├── Makefile                     # Comandos Make
├── manage.sh                    # Script de gestión
├── docker-compose.yml           # Configuración Docker
├── .env.example                 # Variables de entorno
├── .gitignore                   # Git ignore
│
├── docs/                        # 📚 TODA LA DOCUMENTACIÓN
│   ├── INDICE.md               # ← ESTE ARCHIVO
│   ├── RESUMEN_EJECUTIVO.md    # ⭐ Comenzar aquí
│   ├── QUICKSTART.md           # ⭐ Guía rápida
│   ├── CHECKLIST.md            # ⭐ Verificación
│   ├── PLAN_DE_TRABAJO.md      # Roadmap 3 días
│   ├── arquitectura.md         # Diseño técnico
│   ├── DIAGRAMAS.md            # Diagramas visuales
│   ├── NOTAS_IMPLEMENTACION.md # Decisiones de diseño
│   ├── DEBUGGING.md            # Troubleshooting
│   ├── planteamiento.md        # Especificación
│   └── ...pdf                  # Documentos oficiales
│
├── services/                    # 🛠️ SERVICIOS DE LA APLICACIÓN
│   ├── crawler/                # Scrapy spider
│   ├── ingest/                 # Kafka consumer
│   ├── api/                    # Node.js API Gateway
│   └── web/                    # Next.js Frontend
│
└── infra/                       # ⚙️ INFRAESTRUCTURA
    └── scripts/                # Scripts de inicialización
        ├── init-mysql.sql
        └── init-postgres.sql
```

---

## 🎯 Flujo de Lectura Recomendado

### Para Desarrollo (Primera Vez)
1. RESUMEN_EJECUTIVO.md
2. QUICKSTART.md
3. Levantar el sistema (`make start`)
4. CHECKLIST.md (verificar todo funciona)
5. PLAN_DE_TRABAJO.md (entender qué sigue)

### Para Entender el Sistema
1. arquitectura.md
2. DIAGRAMAS.md
3. NOTAS_IMPLEMENTACION.md
4. Revisar código en `services/`

### Para Troubleshooting
1. DEBUGGING.md
2. CHECKLIST.md (verificación)
3. Logs del sistema (`make logs`)

### Para la Presentación
1. RESUMEN_EJECUTIVO.md
2. DIAGRAMAS.md
3. arquitectura.md
4. Demo en vivo con QUICKSTART.md

---

## 📝 Documentos por Propósito

### Inicio Rápido
- RESUMEN_EJECUTIVO.md
- QUICKSTART.md

### Verificación
- CHECKLIST.md

### Planificación
- PLAN_DE_TRABAJO.md

### Diseño
- arquitectura.md
- DIAGRAMAS.md
- NOTAS_IMPLEMENTACION.md

### Operaciones
- DEBUGGING.md
- README.md (raíz)

### Especificación
- planteamiento.md
- Especificación Proyecto Programado BDA.pdf

---

## 🔍 Búsqueda Rápida por Tema

### Docker y Despliegue
- QUICKSTART.md → Paso 2
- README.md → Instalación y Ejecución
- DEBUGGING.md → Troubleshooting

### Bases de Datos
- arquitectura.md → Modelo de Datos
- NOTAS_IMPLEMENTACION.md → Decisiones de Diseño
- DEBUGGING.md → Debugging de Bases de Datos

### Kafka
- arquitectura.md → Procesamiento Asíncrono
- DEBUGGING.md → Debugging de Kafka

### Crawler
- arquitectura.md → Servicios
- NOTAS_IMPLEMENTACION.md → Crawler
- services/crawler/README.md (si existe)

### API
- arquitectura.md → API Gateway
- DEBUGGING.md → Testing de API

### Frontend
- arquitectura.md → Web Frontend
- services/web/README.md (si existe)

### Performance
- NOTAS_IMPLEMENTACION.md → Performance Consideraciones
- DEBUGGING.md → Métricas y Performance

---

## 📚 Documentación Externa Relevante

### Tecnologías Usadas
- **Scrapy**: https://docs.scrapy.org/
- **Kafka**: https://kafka.apache.org/documentation/
- **MySQL**: https://dev.mysql.com/doc/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **MongoDB**: https://docs.mongodb.com/
- **Node.js**: https://nodejs.org/docs/
- **Express**: https://expressjs.com/
- **Next.js**: https://nextjs.org/docs
- **React**: https://react.dev/
- **Docker**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/

---

## 💡 Tips de Navegación

1. **Ctrl+F / Cmd+F** para buscar en documentos
2. Los documentos con ⭐ son los más importantes
3. Todos los documentos están en formato Markdown
4. Los diagramas ASCII se ven mejor en fuente monoespaciada
5. Los comandos de shell se pueden copiar y ejecutar directamente

---

## 🆘 ¿Perdido? Empieza Aquí

```bash
# 1. Lee el resumen ejecutivo
cat docs/RESUMEN_EJECUTIVO.md

# 2. Sigue la guía rápida
cat docs/QUICKSTART.md

# 3. Levanta el sistema
make start

# 4. Verifica que funciona
make health
make stats

# 5. Abre en navegador
open http://localhost:3000
```

---

## 📞 Ayuda Adicional

Si no encuentras lo que buscas:
1. Revisa el README.md principal
2. Busca en DEBUGGING.md
3. Revisa los logs: `make logs`
4. Consulta la especificación original: planteamiento.md

---

_Este índice cubre todos los documentos del proyecto_
_Última actualización: 7 de noviembre, 2025_
