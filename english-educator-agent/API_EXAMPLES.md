# API Usage Examples - English Educator Agent

Este documento contiene ejemplos prácticos de cómo usar la API del sistema.

## 🔐 Autenticación

Por ahora, la API no requiere autenticación. En producción, implementar JWT tokens.

---

## 📊 Endpoints Principales

### 1. Evaluación de Nivel

**Endpoint:** `POST /api/v1/evaluate`

```bash
# Iniciar evaluación
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "initial_message": "Hello, I want to improve my English speaking skills"
  }'
```

**Respuesta:**
```json
{
  "user_id": 1,
  "level": "B1",
  "assessment": {
    "cefr_level": "B1",
    "confidence": 0.85,
    "detailed_breakdown": {
      "vocabulary": "B1",
      "grammar": "A2",
      "fluency": "B1"
    }
  },
  "strengths": ["Good vocabulary range", "Clear pronunciation"],
  "weaknesses": ["Grammar accuracy", "Complex sentences"]
}
```

---

### 2. Crear Lección

**Endpoint:** `POST /api/v1/lesson/create`

```bash
curl -X POST "http://localhost:8000/api/v1/lesson/create" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Present Perfect Tense",
    "level": "B1",
    "user_id": 1
  }'
```

**Respuesta:**
```json
{
  "topic": "Present Perfect Tense",
  "level": "B1",
  "lesson": {
    "objectives": [
      "Understand when to use Present Perfect",
      "Form Present Perfect correctly",
      "Distinguish from Simple Past"
    ],
    "vocabulary": [
      {"word": "already", "definition": "before now"},
      {"word": "yet", "definition": "up to now"}
    ],
    "grammar_focus": {
      "formation": "have/has + past participle",
      "uses": ["life experiences", "recent actions"]
    },
    "examples": [
      "I have visited Paris three times.",
      "She has just finished her homework."
    ],
    "exercises": [...]
  }
}
```

---

### 3. Explicación Gramatical

**Endpoint:** `POST /api/v1/lesson/explain`

```bash
curl -X POST "http://localhost:8000/api/v1/lesson/explain?concept=Present%20Perfect&level=B1"
```

**Respuesta:**
```json
{
  "concept": "Present Perfect",
  "level": "B1",
  "explanation": "The Present Perfect tense connects the past with the present..."
}
```

---

### 4. Obtener Ejemplos

**Endpoint:** `POST /api/v1/lesson/examples`

```bash
curl -X POST "http://localhost:8000/api/v1/lesson/examples?word_or_phrase=phrasal%20verb&context=business"
```

---

### 5. Chat en Tiempo Real (WebSocket)

**JavaScript Example:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/chat/1');

socket.onopen = () => {
  console.log('Connected to chat');
  
  // Send message
  socket.send(JSON.stringify({
    message: "Hi! Can we practice talking about my hobbies?",
    level: "B1",
    topic: "hobbies"
  }));
};

socket.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Reply:', response.reply);
  console.log('Corrections:', response.corrections);
  console.log('New vocabulary:', response.new_vocabulary);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Python Example:**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat/1"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "message": "Hello! I want to practice English.",
            "level": "B1",
            "topic": "daily_life"
        }))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        print(f"AI: {data['reply']}")
        print(f"Corrections: {data['corrections']}")

asyncio.run(chat())
```

---

### 6. Evaluación Interactiva (WebSocket)

```javascript
const evalSocket = new WebSocket('ws://localhost:8000/ws/evaluation/1');

evalSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'question') {
    console.log(`Question ${data.question_number}: ${data.content}`);
    
    // User answers
    const answer = prompt(data.content);
    evalSocket.send(JSON.stringify({
      message: answer
    }));
  }
  
  if (data.type === 'assessment_complete') {
    console.log('Your level:', data.level);
    console.log('Assessment:', data.assessment);
  }
};
```

---

## 📈 Progreso y Reportes

### Obtener Progreso

```bash
curl "http://localhost:8000/api/v1/progress/1?period_days=30"
```

---

## 🧪 Ejercicios

### Generar Ejercicios

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/exercises/generate",
    json={
        "topic": "Past Simple vs Present Perfect",
        "level": "B1",
        "exercise_types": ["multiple_choice", "fill_in_blank"],
        "quantity": 10
    }
)

exercises = response.json()
```

---

## 🔄 Flujo Completo de Usuario

### 1. Nuevo Usuario
```python
import requests
import json

# 1. Evaluación inicial
eval_response = requests.post(
    "http://localhost:8000/api/v1/evaluate",
    json={"user_id": 1, "initial_message": "I want to learn English"}
)
user_level = eval_response.json()["level"]

# 2. Crear lección basada en nivel
lesson_response = requests.post(
    "http://localhost:8000/api/v1/lesson/create",
    json={"topic": "Daily Routines", "level": user_level}
)

# 3. Practicar con conversación (WebSocket)
# Ver ejemplos anteriores

# 4. Ver progreso
progress = requests.get(f"http://localhost:8000/api/v1/progress/1").json()
```

---

## 🐛 Manejo de Errores

### Error Response Format

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 500
}
```

### Errores Comunes

**400 Bad Request:**
```bash
# Falta campo requerido
{
  "error": "Validation error",
  "detail": "Field 'level' is required"
}
```

**500 Internal Server Error:**
```bash
{
  "error": "Internal server error",
  "detail": "LLM request failed"
}
```

---

## 📊 Rate Limiting

Actualmente: 60 requests/minuto por usuario

```bash
# Headers en respuesta
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

---

## 🧰 Herramientas de Testing

### Postman Collection

Importa esta colección en Postman:

```json
{
  "info": {
    "name": "English Educator Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Evaluate User",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\"user_id\": 1, \"initial_message\": \"Hello\"}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/evaluate",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "evaluate"]
        }
      }
    }
  ]
}
```

### cURL Scripts

```bash
# Guardar en test-api.sh
#!/bin/bash

echo "Testing English Educator API..."

# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Create lesson
curl -X POST http://localhost:8000/api/v1/lesson/create \
  -H "Content-Type: application/json" \
  -d '{"topic": "Greetings", "level": "A1"}'

echo "Tests complete!"
```

---

## 📝 Notas Adicionales

### Streaming Responses

Para respuestas en streaming (futuro):
```python
import requests

with requests.post(
    "http://localhost:8000/api/v1/lesson/create",
    json={"topic": "Grammar", "level": "B1"},
    stream=True
) as response:
    for chunk in response.iter_content(chunk_size=8192):
        print(chunk.decode('utf-8'), end='')
```

### Batch Requests

```python
# Múltiples lecciones
topics = ["Grammar", "Vocabulary", "Pronunciation"]
lessons = []

for topic in topics:
    response = requests.post(
        "http://localhost:8000/api/v1/lesson/create",
        json={"topic": topic, "level": "B1"}
    )
    lessons.append(response.json())
```

---

## 🔗 Recursos Adicionales

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/health
