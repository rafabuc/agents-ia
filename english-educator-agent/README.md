# AI English Tutor System

Sistema multi-agente de IA para enseñanza personalizada de inglés, construido con LangGraph, RAG y arquitectura event-driven.

## 🎯 Características

- **Evaluación de Nivel**: Determina nivel CEFR (A1-C2) del estudiante
- **Lecciones Personalizadas**: Contenido adaptado al nivel del estudiante
- **Práctica Conversacional**: Chat en tiempo real con IA
- **Corrección Gramatical**: Feedback detallado y explicaciones
- **Generación de Ejercicios**: Ejercicios adaptativos personalizados
- **Seguimiento de Progreso**: Análisis y reportes de avance

## 🏗️ Arquitectura

```
Frontend (React/Next.js)
    ↓
API Gateway (FastAPI + WebSockets)
    ↓
Multi-Agent System (LangGraph)
    ├── Evaluator Agent
    ├── Tutor Agent
    ├── Grammar Checker
    ├── Conversation Partner
    ├── Exercise Generator
    └── Progress Tracker
    ↓
Data Layer (PostgreSQL + Qdrant + Redis)
    ↓
Event-Driven (Celery + RabbitMQ)
    ↓
Observability (LangSmith + Prometheus + Grafana)
```

## 🚀 Quick Start

### Prerrequisitos

- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (para frontend)
- API Keys: OpenAI, Anthropic

### 1. Clonar y Setup

```bash
git clone <repo-url>
cd english-educator-agent

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

### 2. Levantar Servicios (Docker)

```bash
cd docker
docker-compose up -d
```

Esto levantará:
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- Qdrant (puerto 6333)
- RabbitMQ (puerto 5672, UI en 15672)
- Prometheus (puerto 9090)
- Grafana (puerto 3001)

### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

### 4. Celery Workers

```bash
# En otra terminal
cd backend
source venv/bin/activate

# Worker
celery -A tasks worker --loglevel=info

# Beat scheduler (en otra terminal)
celery -A tasks beat --loglevel=info
```

### 5. Frontend (Opcional)

```bash
cd frontend
npm install
npm run dev
```

## 📁 Estructura del Proyecto

```
english-educator-agent/
├── backend/
│   ├── agents/          # Agentes especializados
│   ├── graphs/          # LangGraph workflows
│   ├── rag/            # Sistema RAG
│   ├── api/            # FastAPI endpoints
│   ├── models/         # SQLAlchemy models
│   ├── tasks/          # Celery tasks
│   └── utils/          # Utilidades
├── data/
│   └── english_content/  # Material educativo
├── docker/
│   └── docker-compose.yml
├── monitoring/
│   ├── grafana/
│   └── prometheus/
└── tests/
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/english_tutor
REDIS_URL=redis://localhost:6379

# Vector DB
QDRANT_URL=http://localhost:6333

# Observability
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=english-tutor

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Coverage
pytest --cov=backend tests/
```

## 📊 Monitoring

### Grafana Dashboard
- URL: http://localhost:3001
- Usuario: admin
- Password: admin

### Prometheus
- URL: http://localhost:9090

### RabbitMQ Management
- URL: http://localhost:15672
- Usuario: admin
- Password: admin

### LangSmith
- URL: https://smith.langchain.com

## 🔄 Uso de la API

### Iniciar Evaluación

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### Crear Lección

```bash
curl -X POST http://localhost:8000/api/v1/lesson/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Present Perfect",
    "level": "B1"
  }'
```

### WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/1');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Hello! I want to practice English.",
    level: "B1",
    topic: "daily_conversation"
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response.reply);
  console.log(response.corrections);
};
```

## 🤖 Agentes Disponibles

### 1. Evaluator Agent
Evalúa el nivel del estudiante (A1-C2) mediante conversación adaptativa.

### 2. Tutor Agent
Crea lecciones personalizadas y explica conceptos gramaticales.

### 3. Grammar Checker
Corrige errores y proporciona explicaciones detalladas.

### 4. Conversation Partner
Mantiene conversaciones naturales adaptadas al nivel del estudiante.

### 5. Exercise Generator
Genera ejercicios personalizados de diversos tipos.

### 6. Progress Tracker
Analiza el progreso y genera reportes detallados.

## 📈 Roadmap

- [x] Sistema multi-agente con LangGraph
- [x] RAG con Qdrant
- [x] Event-driven con Celery
- [x] Observabilidad completa
- [ ] Frontend React completo
- [ ] Speech-to-Text integration
- [ ] Mobile app (React Native)
- [ ] Gamification features
- [ ] Multi-language support

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es parte del curso de Agentes de IA y está disponible bajo licencia MIT.

## 📧 Contacto

Para preguntas y soporte, por favor abre un issue en GitHub.

---

**Built with ❤️ using LangChain, LangGraph, and FastAPI**
