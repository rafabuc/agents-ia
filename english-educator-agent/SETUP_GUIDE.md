# 🚀 Guía de Setup - English Educator Agent

Guía paso a paso para poner en marcha el sistema completo.

## 📋 Pre-requisitos

### Software Necesario
- Python 3.10 o superior
- Docker Desktop
- Git
- Node.js 18+ (opcional, para frontend)
- Un editor de código (VS Code recomendado)

### API Keys Requeridas
- OpenAI API Key (https://platform.openai.com)
- Anthropic API Key (https://console.anthropic.com)
- LangSmith API Key (opcional, para observabilidad) (https://smith.langchain.com)

---

## 🔧 Paso 1: Clonar el Proyecto

```bash
cd C:\workspace\python\MLOPS\DataTalksClub\agents-ia
# El proyecto ya está en: english-educator-agent/
cd english-educator-agent
```

---

## 🔐 Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus API keys
notepad .env
```

Actualiza estas variables:
```env
OPENAI_API_KEY=sk-tu-key-aqui
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
LANGSMITH_API_KEY=ls__tu-key-aqui  # opcional
```

---

## 🐳 Paso 3: Levantar Servicios con Docker

```bash
cd docker
docker-compose up -d
```

Esto iniciará:
- PostgreSQL → `localhost:5432`
- Redis → `localhost:6379`
- Qdrant → `localhost:6333`
- RabbitMQ → `localhost:5672` (UI: `localhost:15672`)
- Prometheus → `localhost:9090`
- Grafana → `localhost:3001`

Verificar servicios:
```bash
docker-compose ps
```

Acceder a UIs:
- **RabbitMQ**: http://localhost:15672 (admin/admin)
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Qdrant**: http://localhost:6333/dashboard

---

## 🐍 Paso 4: Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import langchain; print('✓ LangChain instalado')"
python -c "import langgraph; print('✓ LangGraph instalado')"
```

---

## 🗄️ Paso 5: Inicializar Base de Datos

```bash
# Crear las tablas (cuando tengas modelos de SQLAlchemy)
# python -m alembic upgrade head

# Por ahora, verificar conexión
python -c "from config import settings; print(f'DB URL: {settings.DATABASE_URL}')"
```

---

## ▶️ Paso 6: Iniciar Backend API

```bash
# Asegúrate de estar en /backend con venv activado
uvicorn main:app --reload --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Prueba la API:
- Documentación: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## 🔄 Paso 7: Iniciar Celery Workers

Abre una nueva terminal:

```bash
cd backend
venv\Scripts\activate  # Activar venv

# Worker principal
celery -A tasks worker --loglevel=info --pool=solo
```

Abre otra terminal para el scheduler:

```bash
cd backend
venv\Scripts\activate

# Beat scheduler
celery -A tasks beat --loglevel=info
```

---

## 🧪 Paso 8: Probar el Sistema

### 1. Test de Evaluación de Nivel

```bash
curl -X POST http://localhost:8000/api/v1/evaluate ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": 1, \"initial_message\": \"Hello, I want to improve my English\"}"
```

### 2. Test de Creación de Lección

```bash
curl -X POST http://localhost:8000/api/v1/lesson/create ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Present Perfect Tense\", \"level\": \"B1\"}"
```

### 3. Test de Explicación Gramatical

```bash
curl -X POST "http://localhost:8000/api/v1/lesson/explain?concept=Present%20Perfect&level=B1"
```

### 4. Test WebSocket (Python)

```python
import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://localhost:8000/ws/chat/1"
    
    async with websockets.connect(uri) as websocket:
        # Enviar mensaje
        await websocket.send(json.dumps({
            "message": "Hello! Can you help me practice English?",
            "level": "B1",
            "topic": "daily_conversation"
        }))
        
        # Recibir respuesta
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(test_chat())
```

---

## 📊 Paso 9: Verificar Monitoring

### Prometheus
1. Visita: http://localhost:9090
2. Query: `api_requests_total`
3. Verifica que aparezcan métricas

### Grafana
1. Visita: http://localhost:3001 (admin/admin)
2. Ve a Configuration → Data Sources
3. Add Prometheus: http://prometheus:9090
4. Importa dashboard (opcional)

---

## 🔍 Paso 10: Debugging y Logs

### Ver logs de Backend
```bash
# Los logs aparecen en la terminal donde corre uvicorn
```

### Ver logs de Docker
```bash
cd docker
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f qdrant
```

### Ver logs de Celery
```bash
# En la terminal del worker
# Ver tareas ejecutadas y errores
```

---

## 🧹 Comandos Útiles

### Reiniciar servicios
```bash
cd docker
docker-compose restart
```

### Detener todo
```bash
docker-compose down
```

### Limpiar volúmenes (⚠️ elimina datos)
```bash
docker-compose down -v
```

### Ver uso de recursos
```bash
docker stats
```

---

## ❗ Troubleshooting

### Error: "No module named 'langchain'"
```bash
# Verifica que estés en el venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Connection refused" para Postgres/Redis
```bash
# Verifica que Docker esté corriendo
docker-compose ps

# Reinicia servicios
docker-compose restart postgres redis
```

### Error: "OpenAI API key not found"
```bash
# Verifica .env
cat .env  # Linux/Mac
type .env  # Windows

# Asegúrate que la key esté correcta
```

### Celery no procesa tareas
```bash
# Verifica que RabbitMQ esté corriendo
docker-compose ps rabbitmq

# Reinicia el worker
# Ctrl+C y luego:
celery -A tasks worker --loglevel=info --pool=solo
```

### Puerto 8000 ya en uso
```bash
# Encuentra proceso usando el puerto
netstat -ano | findstr :8000

# Mata el proceso o usa otro puerto
uvicorn main:app --reload --port 8001
```

---

## 📝 Próximos Pasos

Una vez que todo funcione:

1. **Poblar Vector Database**
   - Agrega contenido educativo a `data/english_content/`
   - Ejecuta el script de ingesta (cuando esté implementado)

2. **Crear Modelos de Base de Datos**
   - Define modelos en `backend/models/`
   - Crea migraciones con Alembic

3. **Implementar Frontend** (opcional)
   - Next.js o React
   - Conecta con WebSocket API

4. **Configurar CI/CD**
   - GitHub Actions
   - Deploy automático

5. **Monitoreo Avanzado**
   - Configura alertas en Prometheus
   - Dashboards personalizados en Grafana

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs detalladamente
2. Verifica que todas las dependencias estén instaladas
3. Consulta la documentación oficial de cada herramienta
4. Abre un issue en el repositorio con:
   - Descripción del error
   - Logs relevantes
   - Pasos para reproducir

---

## ✅ Checklist de Verificación

- [ ] Docker Desktop corriendo
- [ ] Servicios Docker levantados (`docker-compose ps`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Entorno virtual Python activado
- [ ] Dependencias instaladas (`pip list`)
- [ ] Backend corriendo (http://localhost:8000/docs)
- [ ] Celery worker activo
- [ ] API responde correctamente (`curl` tests)
- [ ] Prometheus muestra métricas
- [ ] Grafana conectado a Prometheus

---

**🎉 ¡Listo! Ahora tienes un sistema multi-agente de IA funcionando.**

Para más detalles sobre cada componente, consulta:
- `README.md` - Visión general
- `PROYECTO_FINAL_ENGLISH_TUTOR.md` - Arquitectura detallada
- `PROGRAMA_COMPLETO_AGENTES_IA.md` - Curso completo

Happy coding! 🚀
