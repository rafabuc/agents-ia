# ❓ Preguntas Frecuentes (FAQ)

Respuestas a las preguntas más comunes sobre English Educator Agent.

---

## 📋 Índice

- [General](#general)
- [Instalación y Setup](#instalación-y-setup)
- [Uso del Sistema](#uso-del-sistema)
- [Desarrollo](#desarrollo)
- [API y Integración](#api-y-integración)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🌍 General

### ¿Qué es English Educator Agent?

English Educator Agent es un sistema multi-agente de IA diseñado para enseñanza personalizada de inglés. Utiliza 6 agentes especializados que trabajan en conjunto para proporcionar evaluación de nivel, lecciones personalizadas, práctica conversacional, corrección gramatical y seguimiento de progreso.

### ¿Qué tecnologías utiliza?

- **Backend**: Python 3.11, FastAPI
- **Frameworks IA**: LangChain, LangGraph
- **LLMs**: OpenAI GPT-4, Anthropic Claude
- **Base de Datos**: PostgreSQL, Qdrant (vector DB), Redis
- **Mensajería**: RabbitMQ, Celery
- **Monitoring**: Prometheus, Grafana, LangSmith

### ¿Es código abierto?

Sí, el proyecto está bajo licencia MIT. Puedes usar, modificar y distribuir el código libremente.

### ¿Cuánto cuesta ejecutar el sistema?

**Desarrollo local**: Gratis (excepto API calls a LLMs)

**Producción mensual estimado**:
- Infrastructure: $200-500
- LLM API calls: $500-2,000
- Total: ~$700-2,500 (depende del volumen)

---

## 🔧 Instalación y Setup

### ¿Qué necesito para empezar?

**Software:**
- Python 3.10+
- Docker Desktop
- Git

**API Keys:**
- OpenAI API key
- Anthropic API key (opcional)
- LangSmith API key (opcional para tracing)

### ¿Cómo obtengo las API keys?

**OpenAI:**
1. Visita https://platform.openai.com
2. Crea cuenta/inicia sesión
3. Ve a API keys y crea una nueva
4. Copia y guarda en `.env`

**Anthropic:**
1. Visita https://console.anthropic.com
2. Crea cuenta
3. Genera API key
4. Guarda en `.env`

### ¿Funciona en Windows/Mac/Linux?

Sí, el sistema es compatible con:
- ✅ Windows 10/11
- ✅ macOS (Intel y Apple Silicon)
- ✅ Linux (Ubuntu, Debian, etc.)

### ¿Puedo usar solo OpenAI o solo Anthropic?

Sí. El sistema está configurado para usar ambos, pero puedes:
- Solo OpenAI: Funciona completamente
- Solo Anthropic: Funciona completamente
- Ambos: Mejor experiencia (recomendado)

### El setup demora mucho, ¿es normal?

Sí, la primera vez puede tomar 10-15 minutos:
- Docker descarga imágenes (~5 min)
- Python instala dependencias (~3 min)
- Inicialización de servicios (~2 min)

---

## 💻 Uso del Sistema

### ¿Cómo evalúo el nivel de un estudiante?

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "initial_message": "Hello"}'
```

O usa el endpoint WebSocket para evaluación interactiva.

### ¿Puedo personalizar las lecciones?

Sí, puedes:
1. Modificar prompts en `backend/utils/prompts.py`
2. Agregar contenido educativo en `data/english_content/`
3. Ajustar parámetros del agente tutor

### ¿Cuántos estudiantes puede manejar simultáneamente?

**Desarrollo**: 10-20 usuarios concurrentes
**Producción** (con scaling): 1,000+ usuarios concurrentes

Depende de la infraestructura y configuración.

### ¿El sistema soporta otros idiomas?

Actualmente está diseñado para enseñar inglés. Para otros idiomas:
- Modificar contenido educativo
- Ajustar prompts de agentes
- Actualizar evaluaciones CEFR

---

## 👨‍💻 Desarrollo

### ¿Cómo agrego un nuevo agente?

1. Crear archivo en `backend/agents/nuevo_agente.py`
2. Implementar clase heredando de estructura base
3. Registrar en supervisor (`backend/graphs/supervisor.py`)
4. Agregar tests en `tests/unit/`
5. Actualizar documentación

### ¿Cómo funciona el sistema RAG?

1. Contenido educativo se vectoriza con OpenAI embeddings
2. Se almacena en Qdrant (vector database)
3. Queries buscan contenido similar semánticamente
4. Resultados se re-rankean con LLM
5. Contenido relevante se usa para generar respuestas

### ¿Puedo cambiar el modelo de LLM?

Sí, edita `backend/config.py`:

```python
DEFAULT_GPT_MODEL = "gpt-4o"  # Cambiar a "gpt-4-turbo", "gpt-3.5-turbo", etc.
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Cambiar versión
```

### ¿Cómo debuggeo los agentes?

1. **LangSmith**: Tracing automático si configurado
2. **Logs**: Ver terminal donde corre uvicorn
3. **Debugger**: Usa VS Code o PyCharm debugger
4. **Print debugging**: Agregar `logger.info()` o `print()`

### ¿Dónde están los tests?

```
tests/
├── unit/           # Tests unitarios de agentes
├── integration/    # Tests de API y workflows
└── e2e/           # Tests end-to-end
```

Ejecutar: `pytest tests/ -v`

---

## 🔌 API y Integración

### ¿Tiene documentación de API?

Sí, cuando el sistema está corriendo:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Ejemplos**: Ver `API_EXAMPLES.md`

### ¿Soporta WebSockets?

Sí, para chat en tiempo real:
- Chat: `ws://localhost:8000/ws/chat/{user_id}`
- Evaluación: `ws://localhost:8000/ws/evaluation/{user_id}`

### ¿Hay rate limiting?

Configurado en `backend/config.py`:
```python
RATE_LIMIT_PER_MINUTE = 60  # requests por minuto
```

### ¿Cómo integro con mi aplicación?

1. **REST API**: Consume endpoints HTTP estándar
2. **WebSocket**: Para features en tiempo real
3. **SDK**: (futuro) Cliente Python/JavaScript

### ¿Puedo usar solo la API sin frontend?

Sí, la API es independiente. Puedes:
- Usar solo backend
- Construir tu propio frontend
- Integrar con aplicaciones existentes

---

## 🚀 Deployment

### ¿Cómo despliego en producción?

Ver `DEPLOYMENT_CHECKLIST.md` para guía completa.

Opciones:
1. **Docker Compose**: Para servidores simples
2. **Kubernetes**: Para producción escalable
3. **Cloud managed**: AWS ECS, GCP Cloud Run, Azure Container Apps

### ¿Qué servicios cloud recomiendan?

**Recomendados:**
- **AWS**: EKS (Kubernetes), RDS (PostgreSQL), ElastiCache (Redis)
- **GCP**: GKE, Cloud SQL, Memorystore
- **Azure**: AKS, Azure Database, Azure Cache

### ¿Necesito Kubernetes?

No es obligatorio:
- **Desarrollo**: Docker Compose suficiente
- **Producción pequeña**: Docker Compose + servidor
- **Producción grande**: Kubernetes recomendado

### ¿Cómo escalo el sistema?

**Horizontal scaling:**
1. Aumentar réplicas de backend
2. Agregar workers de Celery
3. Usar load balancer

**Vertical scaling:**
1. Aumentar recursos de containers
2. Optimizar queries de DB
3. Implementar caching agresivo

### ¿Cómo hago backups?

**Base de Datos:**
```bash
# PostgreSQL
pg_dump english_tutor > backup.sql

# Automatizar con cron
0 2 * * * pg_dump english_tutor > /backups/daily.sql
```

**Vector DB (Qdrant):**
- Usar snapshots de Qdrant
- Backup de volumen Docker
- Re-ingestar contenido si es necesario

---

## 🔍 Troubleshooting

### Error: "Module not found"

```bash
# Asegurar que estás en el venv
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Connection refused" (PostgreSQL/Redis)

```bash
# Verificar servicios Docker
cd docker && docker-compose ps

# Reiniciar servicios
docker-compose restart postgres redis

# Ver logs
docker-compose logs postgres
```

### Los agentes no responden

**Posibles causas:**
1. API keys inválidas o expiradas
2. Límite de rate de API alcanzado
3. Servicios Docker no corriendo
4. Error en configuración `.env`

**Solución:**
```bash
# Verificar .env
cat .env

# Verificar servicios
docker-compose ps

# Ver logs del backend
# (en terminal donde corre uvicorn)
```

### Error: "No module named 'langchain'"

Estás ejecutando fuera del venv:

```bash
# Activar venv primero
cd backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Luego ejecutar
python main.py
```

### WebSocket se desconecta

**Causas comunes:**
1. Timeout de inactividad
2. Proxy/firewall bloqueando
3. Error en el agente (ver logs)

**Solución:**
- Implementar heartbeat/ping
- Aumentar timeout
- Revisar logs del servidor

### Qdrant no encuentra contenido

```bash
# Primero, ingestar contenido
cd backend
python -m rag.ingest

# Verificar colección
curl http://localhost:6333/collections/english_content
```

### Celery no procesa tareas

```bash
# Verificar RabbitMQ
docker-compose ps rabbitmq

# Ver logs de Celery
# (en terminal donde corre el worker)

# Reiniciar worker
# Ctrl+C y luego:
celery -A tasks worker --loglevel=info
```

### Error: "Port already in use"

```bash
# Windows: Ver qué usa el puerto
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Matar proceso o usar otro puerto
uvicorn main:app --port 8001
```

### Tests fallan

```bash
# Asegurar servicios Docker corriendo
docker-compose ps

# Verificar variables de entorno
cat .env

# Ejecutar tests específicos
pytest tests/unit/test_evaluator_agent.py -v

# Ver output completo
pytest tests/ -vv -s
```

---

## 📊 Performance

### ¿Cuál es la latencia esperada?

**Típico:**
- API REST: 100-500ms
- LLM calls: 1-5 segundos
- WebSocket chat: 2-8 segundos (dependiendo del agente)

### ¿Cómo reduzco costos de LLM?

1. **Caching**: Cachear respuestas comunes
2. **Modelos más baratos**: Usar GPT-3.5 donde sea posible
3. **Batch requests**: Agrupar llamadas
4. **Prompt optimization**: Reducir tokens en prompts
5. **Fallback**: Usar modelos locales para tareas simples

### ¿Puedo usar modelos locales?

Sí, puedes integrar:
- **Llama 2/3**: Con Ollama o LlamaCPP
- **Mistral**: Via Ollama
- **Custom models**: Implementar wrapper

Editar `backend/agents/` para usar modelos locales.

---

## 🔐 Seguridad

### ¿Cómo protejo las API keys?

1. **Nunca** commitear `.env` a git
2. Usar **secrets manager** en producción
3. Rotar keys regularmente
4. Implementar **rate limiting**
5. Usar **HTTPS** en producción

### ¿El sistema es seguro para producción?

**Implementado:**
- ✅ Input validation
- ✅ Error handling
- ✅ CORS configurado
- ✅ Environment variables

**Por implementar:**
- ⏳ Authentication (JWT)
- ⏳ Authorization (RBAC)
- ⏳ Encryption at rest
- ⏳ Security audit

### ¿Hay autenticación?

Actualmente no. Para añadir:
1. Implementar JWT tokens
2. Agregar middleware de auth
3. Proteger endpoints sensibles

Ver `backend/api/middleware.py` para comenzar.

---

## 📈 Roadmap

### ¿Qué viene después?

**Q1 2025:**
- Frontend web completo
- Mobile app (React Native)
- Speech-to-text integration

**Q2 2025:**
- Gamification
- Social features
- Multi-language support

### ¿Puedo sugerir features?

¡Sí! Abre un issue en GitHub con:
- Descripción del feature
- Caso de uso
- Beneficio esperado

Ver `CONTRIBUTING.md` para detalles.

---

## 💬 Soporte

### ¿Dónde obtengo ayuda?

1. **Documentación**: Primero revisa docs completa
2. **GitHub Issues**: Para bugs y features
3. **Discord**: Para chat en tiempo real
4. **Email**: support@english-tutor-ai.com

### ¿Hay comunidad?

- **GitHub Discussions**: Para Q&A
- **Discord Server**: Para chat
- **Twitter**: @EnglishTutorAI
- **Blog**: blog.english-tutor-ai.com

### ¿Ofrecen consultoría?

Para deployment enterprise o customización:
- Email: enterprise@english-tutor-ai.com
- Consultoría disponible
- Custom development
- Training y soporte

---

## 🎓 Aprendizaje

### ¿Hay tutoriales?

Sí:
- `SETUP_GUIDE.md`: Setup paso a paso
- `API_EXAMPLES.md`: Ejemplos de API
- `PROGRAMA_COMPLETO_AGENTES_IA.md`: Curso completo

### ¿Dónde aprendo sobre agentes de IA?

Recursos recomendados:
1. **Nuestro curso**: `PROGRAMA_COMPLETO_AGENTES_IA.md`
2. **LangChain docs**: https://python.langchain.com
3. **LangGraph docs**: https://langchain-ai.github.io/langgraph/
4. **DeepLearning.AI**: Cursos de agentes

### ¿Puedo usar esto para aprender?

¡Absolutamente! El proyecto es:
- Código bien documentado
- Arquitectura clara
- Tests comprensivos
- Multiple use cases

Ideal para aprender sobre:
- Multi-agent systems
- LangChain/LangGraph
- RAG implementation
- Production LLM apps

---

## 📝 Licencia y Legal

### ¿Puedo usar esto comercialmente?

Sí, bajo licencia MIT puedes:
- ✅ Usar comercialmente
- ✅ Modificar
- ✅ Distribuir
- ✅ Uso privado

Requisitos:
- Incluir aviso de copyright
- Incluir licencia MIT

### ¿Tengo que compartir mis cambios?

No es obligatorio. MIT permite:
- Código privado
- Modificaciones propietarias
- No requirement de contribuir cambios

Pero contribuciones son ¡bienvenidas! 🎉

---

## ❓ Otras Preguntas

### No encontré mi pregunta

1. Busca en **GitHub Issues** (open y closed)
2. Pregunta en **Discord**
3. Abre un **nuevo issue** con tag "question"

### ¿Cómo reporto un bug?

Ver `CONTRIBUTING.md` sección "Reportar Bugs"

Template de bug report en GitHub Issues.

### ¿Puedo contribuir?

¡Sí! Ver `CONTRIBUTING.md` para:
- Guías de contribución
- Code style
- Pull request process

---

**¿Tienes más preguntas?**

👉 [Abrir un Issue](https://github.com/REPO/issues/new)
👉 [Únete a Discord](https://discord.gg/INVITE)
👉 [Email](mailto:support@english-tutor-ai.com)

---

*Última actualización: 2024*
*FAQ en constante actualización basado en preguntas de la comunidad*
