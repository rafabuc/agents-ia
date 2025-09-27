# Proyecto Final: AI English Tutor System
## Agente Multi-Modal para Enseñanza de Inglés

---

## 📋 Visión General del Proyecto

### Objetivo
Construir un sistema completo de agentes de IA para enseñanza personalizada de inglés que incluya:
- Evaluación de nivel
- Lecciones personalizadas
- Práctica conversacional
- Corrección gramatical
- Seguimiento de progreso
- Generación de ejercicios

### Arquitectura High-Level
```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Chat UI  │  │Dashboard │  │ Exercises Portal │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ WebSocket + REST
┌────────────────────────▼────────────────────────────┐
│              API Gateway (FastAPI)                   │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│           Multi-Agent System (LangGraph)            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Evaluator  │  │    Tutor     │  │  Grammar  │ │
│  │    Agent     │  │    Agent     │  │  Checker  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │Conversation  │  │   Exercise   │  │  Progress │ │
│  │   Partner    │  │  Generator   │  │  Tracker  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Data Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │PostgreSQL│  │  Qdrant  │  │  Redis Cache     │  │
│  │(User Data│  │ (RAG for │  │                  │  │
│  │ Progress)│  │ content) │  │                  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│              Event-Driven Layer                      │
│  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │   Celery     │  │      RabbitMQ Queue          │ │
│  │  Workers     │  │  (Async Tasks & Scheduling)  │ │
│  └──────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│            Observability Stack                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │LangSmith │  │Prometheus│  │     Grafana      │  │
│  │ Tracing  │  │ Metrics  │  │   Dashboards     │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🏗️ Fase 1: Setup del Proyecto (Semana 1)

### 1.1 Estructura de Directorios

```bash
english-tutor-ai/
├── backend/
│   ├── agents/              # Agentes de LangGraph
│   │   ├── __init__.py
│   │   ├── evaluator.py     # Evaluación de nivel
│   │   ├── tutor.py         # Tutor principal
│   │   ├── grammar.py       # Corrección gramatical
│   │   ├── conversation.py  # Partner conversacional
│   │   ├── exercise.py      # Generador de ejercicios
│   │   └── progress.py      # Tracker de progreso
│   ├── graphs/              # LangGraph workflows
│   │   ├── __init__.py
│   │   ├── main_graph.py    # Orquestador principal
│   │   └── supervisor.py    # Supervisor de agentes
│   ├── rag/                 # RAG system
│   │   ├── __init__.py
│   │   ├── ingest.py        # Ingesta de contenido
│   │   ├── retrieval.py     # Retrieval logic
│   │   └── embeddings.py    # Gestión de embeddings
│   ├── api/                 # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── websockets.py
│   │   └── middleware.py
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   └── progress.py
│   ├── tasks/               # Celery tasks
│   │   ├── __init__.py
│   │   ├── daily_practice.py
│   │   └── progress_report.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── prompts.py       # Prompt templates
│   │   └── helpers.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   ├── package.json
│   └── ...
├── data/
│   ├── english_content/     # Material educativo
│   │   ├── grammar/
│   │   ├── vocabulary/
│   │   └── exercises/
│   └── processed/           # Vectorized data
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── Dockerfile.worker
│   └── docker-compose.yml
├── k8s/                     # Kubernetes manifests
│   ├── deployments/
│   ├── services/
│   └── ingress/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── monitoring/
│   ├── grafana/
│   │   └── dashboards/
│   └── prometheus/
│       └── rules/
├── .env.example
├── README.md
└── pyproject.toml
```

### 1.2 Setup Inicial

```bash
# Crear proyecto
mkdir english-tutor-ai && cd english-tutor-ai

# Backend setup
python -m venv venv
source venv/bin/activate
pip install langchain langgraph langchain-openai langchain-anthropic
pip install fastapi uvicorn websockets
pip install sqlalchemy asyncpg psycopg2-binary
pip install celery redis
pip install qdrant-client sentence-transformers
pip install python-dotenv pydantic-settings
pip install langsmith phoenix-arize

# Frontend setup (Next.js + TypeScript)
npx create-next-app@latest frontend --typescript --tailwind --app

# Servicios con Docker Compose
touch docker/docker-compose.yml
```

### 1.3 Configuración Base

**`.env`**
```env
# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/english_tutor
REDIS_URL=redis://localhost:6379

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional

# Observability
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=english-tutor

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**`docker/docker-compose.yml`**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: english_tutor
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  prometheus_data:
  grafana_data:
```

---

## 🤖 Fase 2: Arquitectura de Agentes (Semanas 2-3)

### 2.1 Definición de Agentes Especializados

#### **Agent 1: Evaluator Agent** (Evaluación de Nivel)
**Responsabilidad:** Determinar el nivel CEFR (A1-C2) del estudiante

```python
# backend/agents/evaluator.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from typing import TypedDict, List

class EvaluatorState(TypedDict):
    messages: List
    student_level: str
    strengths: List[str]
    weaknesses: List[str]
    conversation_history: List

EVALUATOR_PROMPT = """You are an expert English language evaluator following the CEFR framework.

Conduct a natural conversation to assess the student's level across these dimensions:
- Vocabulary range and accuracy
- Grammar complexity and correctness
- Fluency and coherence
- Pronunciation patterns (from text analysis)
- Comprehension abilities

Ask 5-7 progressively challenging questions. Start simple, then adapt based on responses.

Current question #{question_num}:
{question}

Student response: {response}

Provide your assessment in JSON format:
{{
  "cefr_level": "A1|A2|B1|B2|C1|C2",
  "confidence": 0.0-1.0,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "next_question": "question text" or null if complete
}}
"""

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(EvaluatorState)
        
        workflow.add_node("ask_question", self.ask_question)
        workflow.add_node("analyze_response", self.analyze_response)
        workflow.add_node("determine_level", self.determine_level)
        
        workflow.set_entry_point("ask_question")
        workflow.add_edge("ask_question", "analyze_response")
        workflow.add_conditional_edges(
            "analyze_response",
            self.should_continue,
            {
                "continue": "ask_question",
                "finish": "determine_level"
            }
        )
        workflow.add_edge("determine_level", "__end__")
        
        return workflow.compile()
    
    async def ask_question(self, state: EvaluatorState):
        question_num = len(state["conversation_history"]) + 1
        
        # Generar pregunta adaptativa
        response = await self.llm.ainvoke([
            SystemMessage(content="Generate an appropriate evaluation question."),
            HumanMessage(content=f"Question #{question_num}, previous: {state['conversation_history']}")
        ])
        
        return {"messages": [response.content]}
    
    async def analyze_response(self, state: EvaluatorState):
        # Análisis de respuesta del estudiante
        analysis = await self.llm.ainvoke([
            SystemMessage(content=EVALUATOR_PROMPT),
            HumanMessage(content=str(state["messages"][-1]))
        ])
        
        return {"conversation_history": state["conversation_history"] + [analysis]}
    
    def should_continue(self, state: EvaluatorState):
        if len(state["conversation_history"]) >= 7:
            return "finish"
        return "continue"
    
    async def determine_level(self, state: EvaluatorState):
        # Consolidar evaluación final
        final_analysis = await self.llm.ainvoke([
            SystemMessage(content="Provide final CEFR assessment from conversation."),
            HumanMessage(content=str(state["conversation_history"]))
        ])
        
        return {
            "student_level": final_analysis["cefr_level"],
            "strengths": final_analysis["strengths"],
            "weaknesses": final_analysis["weaknesses"]
        }
```

#### **Agent 2: Tutor Agent** (Tutor Principal)
**Responsabilidad:** Explicar conceptos, crear lecciones personalizadas

```python
# backend/agents/tutor.py
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

class TutorAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.7)
        self.tools = [
            self.create_lesson,
            self.explain_grammar,
            self.provide_examples
        ]
    
    @tool
    def create_lesson(self, topic: str, level: str) -> dict:
        """Create a personalized lesson for the given topic and level"""
        prompt = f"""Create a comprehensive {level}-level lesson on: {topic}

        Include:
        1. Learning objectives (3-5 points)
        2. Key vocabulary (10-15 words with definitions)
        3. Grammar focus (if applicable)
        4. Examples and usage
        5. Practice exercises (5)
        6. Cultural notes (if relevant)
        
        Format as structured JSON."""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    @tool
    def explain_grammar(self, concept: str, level: str) -> str:
        """Explain a grammar concept with examples"""
        prompt = f"""Explain {concept} for {level} level students.
        
        Structure:
        1. Simple definition
        2. Formation/Rules
        3. 3 example sentences
        4. Common mistakes to avoid
        5. Practice tip"""
        
        return self.llm.invoke(prompt).content
    
    @tool
    def provide_examples(self, word_or_phrase: str, context: str) -> List[str]:
        """Provide contextual examples"""
        prompt = f"""Give 5 example sentences using "{word_or_phrase}" in {context} context.
        
        Vary:
        - Sentence complexity
        - Tenses
        - Formality levels"""
        
        return self.llm.invoke(prompt).content
```

#### **Agent 3: Grammar Checker Agent**
**Responsabilidad:** Corrección gramatical con explicaciones

```python
# backend/agents/grammar.py
from langchain_openai import ChatOpenAI
import json

class GrammarCheckerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    
    async def check_grammar(self, text: str, student_level: str) -> dict:
        prompt = f"""Analyze this text for grammar errors. Student level: {student_level}

Text: "{text}"

Provide detailed feedback in JSON:
{{
  "corrections": [
    {{
      "original": "incorrect phrase",
      "corrected": "correct phrase",
      "error_type": "subject-verb agreement",
      "explanation": "Simple explanation why it's wrong",
      "rule": "Grammar rule reference"
    }}
  ],
  "overall_quality": {{
    "score": 0-100,
    "strengths": ["point1", "point2"],
    "improvements": ["suggestion1", "suggestion2"]
  }},
  "vocabulary_feedback": {{
    "used_well": ["word1", "word2"],
    "could_improve": [
      {{"word": "basic word", "suggestion": "more sophisticated alternative"}}
    ]
  }}
}}"""
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)
    
    async def explain_error(self, error_type: str, example: str) -> str:
        """Deep dive explanation of specific error"""
        prompt = f"""Explain {error_type} error in detail.
        
        Student's mistake: {example}
        
        Provide:
        1. Why it's wrong
        2. Correct form
        3. Rule explanation
        4. 3 more examples
        5. Memory tip"""
        
        return (await self.llm.ainvoke(prompt)).content
```

#### **Agent 4: Conversation Partner Agent**
**Responsabilidad:** Práctica conversacional natural

```python
# backend/agents/conversation.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage

class ConversationPartnerAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.9)
        self.conversation_memory = []
    
    async def chat(self, user_message: str, context: dict) -> dict:
        """Natural conversation with pedagogical intent"""
        
        system_context = f"""You are a friendly English conversation partner.

Student profile:
- Level: {context['level']}
- Current topic: {context.get('topic', 'general')}
- Learning goals: {context.get('goals', [])}

Guidelines:
- Match your language complexity to their level
- Gently correct major errors in your response
- Ask follow-up questions to encourage speaking
- Introduce new vocabulary occasionally
- Be encouraging and supportive"""

        response = await self.llm.ainvoke([
            {"role": "system", "content": system_context},
            *self.conversation_memory,
            {"role": "user", "content": user_message}
        ])
        
        # Analyze user's message for errors
        analysis = await self._analyze_message(user_message, context['level'])
        
        self.conversation_memory.append(HumanMessage(content=user_message))
        self.conversation_memory.append(AIMessage(content=response.content))
        
        return {
            "reply": response.content,
            "corrections": analysis['corrections'],
            "new_vocabulary": analysis['vocabulary_introduced'],
            "engagement_score": analysis['engagement_score']
        }
    
    async def _analyze_message(self, message: str, level: str):
        # Background analysis sin interrumpir conversación
        pass
```

#### **Agent 5: Exercise Generator Agent**
**Responsabilidad:** Crear ejercicios personalizados

```python
# backend/agents/exercise.py
from langchain_openai import ChatOpenAI
from enum import Enum

class ExerciseType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_in_blank"
    SENTENCE_REORDER = "sentence_reorder"
    TRANSLATION = "translation"
    WRITING_PROMPT = "writing_prompt"

class ExerciseGeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    async def generate_exercise_set(
        self, 
        topic: str, 
        level: str, 
        exercise_types: List[ExerciseType],
        quantity: int = 10
    ) -> List[dict]:
        """Generate diverse exercise set"""
        
        exercises = []
        for ex_type in exercise_types:
            prompt = self._get_exercise_prompt(ex_type, topic, level, quantity)
            response = await self.llm.ainvoke(prompt)
            exercises.extend(self._parse_exercises(response.content, ex_type))
        
        return exercises
    
    def _get_exercise_prompt(self, ex_type: ExerciseType, topic: str, level: str, qty: int):
        if ex_type == ExerciseType.MULTIPLE_CHOICE:
            return f"""Create {qty} multiple choice questions about {topic} for {level} level.

Format each as JSON:
{{
  "question": "Question text",
  "options": ["A", "B", "C", "D"],
  "correct": "B",
  "explanation": "Why B is correct"
}}"""
        
        elif ex_type == ExerciseType.FILL_BLANK:
            return f"""Create {qty} fill-in-the-blank exercises for {topic} ({level} level).

Format:
{{
  "sentence": "The cat ___ on the mat.",
  "answer": "sat",
  "alternatives": ["sits", "sitting"],
  "hint": "past tense of 'sit'"
}}"""
        
        # ... más tipos
    
    async def generate_writing_prompt(self, level: str, interests: List[str]) -> dict:
        """Generate creative writing prompt"""
        prompt = f"""Create an engaging writing prompt for {level} level student.

Interests: {', '.join(interests)}

Include:
1. Prompt text (2-3 sentences)
2. Suggested word count
3. Key vocabulary to use (5-7 words)
4. Grammar focus
5. Evaluation criteria"""
        
        return await self.llm.ainvoke(prompt)
```

#### **Agent 6: Progress Tracker Agent**
**Responsabilidad:** Analizar progreso y generar reportes

```python
# backend/agents/progress.py
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class ProgressTrackerAgent:
    def __init__(self, db: Session):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = db
    
    async def generate_progress_report(self, user_id: int, period_days: int = 30) -> dict:
        """Generate comprehensive progress report"""
        
        # Obtener datos del usuario
        user_data = self._fetch_user_data(user_id, period_days)
        
        report_prompt = f"""Analyze student progress and generate report.

Data:
- Sessions: {user_data['session_count']}
- Total study time: {user_data['total_minutes']} minutes
- Exercises completed: {user_data['exercises_completed']}
- Accuracy: {user_data['avg_accuracy']}%
- Grammar improvements: {user_data['grammar_corrections']}
- Vocabulary acquired: {user_data['new_words']}

Generate JSON report:
{{
  "summary": "Overall progress narrative",
  "achievements": ["achievement1", "achievement2"],
  "improvements": [
    {{"area": "grammar", "change": "+15%", "details": "..."}}
  ],
  "challenges": ["challenge1", "challenge2"],
  "recommendations": [
    {{"focus_area": "vocabulary", "action": "Practice collocations", "priority": "high"}}
  ],
  "next_level_readiness": {{
    "current": "B1",
    "next": "B2",
    "readiness_score": 0.65,
    "estimated_time": "2-3 months"
  }}
}}"""
        
        response = await self.llm.ainvoke(report_prompt)
        return json.loads(response.content)
    
    async def track_session(self, session_data: dict):
        """Real-time progress tracking during session"""
        # Guardar en DB y actualizar métricas
        pass
```

### 2.2 Supervisor y Orquestación con LangGraph

```python
# backend/graphs/supervisor.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class SupervisorState(TypedDict):
    user_message: str
    user_context: dict
    next_agent: str
    agent_responses: dict
    final_response: str

class SupervisorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.agents = {
            "evaluator": EvaluatorAgent(),
            "tutor": TutorAgent(),
            "grammar": GrammarCheckerAgent(),
            "conversation": ConversationPartnerAgent(),
            "exercise": ExerciseGeneratorAgent(),
            "progress": ProgressTrackerAgent()
        }
        self.graph = self._create_graph()
    
    def _create_graph(self):
        workflow = StateGraph(SupervisorState)
        
        # Agregar nodos
        workflow.add_node("supervisor", self.route_to_agent)
        workflow.add_node("evaluator", self.agents["evaluator"].run)
        workflow.add_node("tutor", self.agents["tutor"].run)
        workflow.add_node("grammar", self.agents["grammar"].check_grammar)
        workflow.add_node("conversation", self.agents["conversation"].chat)
        workflow.add_node("exercise", self.agents["exercise"].generate_exercise_set)
        workflow.add_node("synthesize", self.synthesize_response)
        
        # Entry point
        workflow.set_entry_point("supervisor")
        
        # Routing condicional
        workflow.add_conditional_edges(
            "supervisor",
            self.determine_next_agent,
            {
                "evaluator": "evaluator",
                "tutor": "tutor",
                "grammar": "grammar",
                "conversation": "conversation",
                "exercise": "exercise",
                "end": "synthesize"
            }
        )
        
        # Todos los agentes van a synthesize
        for agent in ["evaluator", "tutor", "grammar", "conversation", "exercise"]:
            workflow.add_edge(agent, "synthesize")
        
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    async def route_to_agent(self, state: SupervisorState):
        """Supervisor decide qué agente usar"""
        
        routing_prompt = f"""Analyze the user request and determine which agent(s) should handle it.

User message: "{state['user_message']}"
User context: {state['user_context']}

Available agents:
- evaluator: Assess student's level (initial evaluation)
- tutor: Explain concepts, create lessons
- grammar: Check and correct grammar
- conversation: Natural conversation practice
- exercise: Generate practice exercises

Respond with JSON:
{{
  "primary_agent": "agent_name",
  "secondary_agents": ["agent1", "agent2"],
  "reasoning": "Why this routing"
}}"""
        
        response = await self.llm.ainvoke(routing_prompt)
        routing = json.loads(response.content)
        
        return {"next_agent": routing["primary_agent"]}
    
    def determine_next_agent(self, state: SupervisorState) -> str:
        return state["next_agent"]
    
    async def synthesize_response(self, state: SupervisorState):
        """Combinar respuestas de múltiples agentes"""
        
        synthesis_prompt = f"""Synthesize agent responses into coherent user reply.

Agent responses: {state['agent_responses']}
User context: {state['user_context']}

Create natural, helpful response that:
1. Answers user's question
2. Includes relevant feedback
3. Encourages continued learning
4. Suggests next steps"""
        
        final = await self.llm.ainvoke(synthesis_prompt)
        return {"final_response": final.content}
```

---

## 📚 Fase 3: Sistema RAG (Semana 4)

### 3.1 Preparación de Contenido Educativo

```python
# backend/rag/ingest.py
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class ContentIngestor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "english_content"
        
    async def ingest_educational_content(self, content_dir: str):
        """Ingest and vectorize educational materials"""
        
        # Crear colección si no existe
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        
        # Cargar documentos
        loader = DirectoryLoader(
            content_dir,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        # Chunking estratégico
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        # Metadata enrichment
        for chunk in chunks:
            chunk.metadata.update({
                "topic": self._extract_topic(chunk.page_content),
                "level": self._determine_level(chunk.page_content),
                "type": self._categorize_content(chunk.page_content)
            })
        
        # Vectorización y upload
        points = []
        for idx, chunk in enumerate(chunks):
            embedding = await self.embeddings.aembed_query(chunk.page_content)
            points.append(
                PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={
                        "text": chunk.page_content,
                        "metadata": chunk.metadata
                    }
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"Ingested {len(chunks)} chunks")
    
    def _extract_topic(self, text: str) -> str:
        # Usar LLM para extraer topic principal
        pass
    
    def _determine_level(self, text: str) -> str:
        # Analizar complejidad → CEFR level
        pass
```

### 3.2 Retrieval Avanzado

```python
# backend/rag/retrieval.py
from typing import List, Dict
from langchain_core.documents import Document

class AdvancedRetriever:
    def __init__(self, client: QdrantClient, embeddings: OpenAIEmbeddings):
        self.client = client
        self.embeddings = embeddings
        self.collection_name = "english_content"
    
    async def hybrid_search(
        self, 
        query: str, 
        student_level: str,
        filters: dict = None,
        k: int = 5
    ) -> List[Document]:
        """Hybrid dense + filtered search"""
        
        # Dense vector search
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Build filters
        must_conditions = [
            {"key": "metadata.level", "match": {"value": student_level}}
        ]
        
        if filters:
            if "topic" in filters:
                must_conditions.append({
                    "key": "metadata.topic", 
                    "match": {"value": filters["topic"]}
                })
        
        # Search con filtros
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter={"must": must_conditions} if must_conditions else None,
            limit=k
        )
        
        # Re-ranking con cross-encoder
        reranked = await self._rerank(query, results)
        
        return [
            Document(
                page_content=r.payload["text"],
                metadata=r.payload["metadata"]
            )
            for r in reranked
        ]
    
    async def multi_query_retrieval(self, query: str, student_level: str) -> List[Document]:
        """Generate multiple queries for better coverage"""
        
        # Generar variaciones de query
        query_variations = await self._generate_query_variations(query)
        
        all_results = []
        for q in query_variations:
            results = await self.hybrid_search(q, student_level, k=3)
            all_results.extend(results)
        
        # Deduplicar y rankear
        unique_results = self._deduplicate(all_results)
        return unique_results[:5]
    
    async def _generate_query_variations(self, original_query: str) -> List[str]:
        """LLM generates query variations"""
        llm = ChatOpenAI(model="gpt-4o-mini")
        prompt = f"""Generate 3 alternative phrasings of this query for better retrieval:
        
Original: "{original_query}"

Return only the 3 variations, one per line."""
        
        response = await llm.ainvoke(prompt)
        return response.content.strip().split("\n")
    
    async def _rerank(self, query: str, results: List) -> List:
        """Re-rank with cross-encoder or LLM"""
        # Implementar re-ranking
        return results  # Simplified
```

### 3.3 Integración RAG con Agentes

```python
# Ejemplo en TutorAgent
class TutorAgent:
    def __init__(self, retriever: AdvancedRetriever):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.retriever = retriever
    
    async def create_lesson_with_rag(self, topic: str, level: str) -> dict:
        """Create lesson augmented with retrieved content"""
        
        # Retrieve relevant content
        relevant_docs = await self.retriever.hybrid_search(
            query=f"lesson plan {topic}",
            student_level=level,
            filters={"type": "lesson"},
            k=5
        )
        
        # Build context
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        prompt = f"""Create a comprehensive lesson on {topic} for {level} level.

Retrieved educational content:
{context}

Create original lesson that:
1. Uses retrieved content as reference
2. Adapts to {level} level specifically
3. Includes interactive elements
4. Provides clear examples

Format as structured JSON with sections: objectives, content, examples, exercises."""
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)
```

---

## 🔄 Fase 4: Event-Driven Architecture (Semana 5)

### 4.1 Configuración de Celery

```python
# backend/tasks/__init__.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "english_tutor",
    broker="amqp://admin:admin@localhost:5672//",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "daily-practice-reminder": {
            "task": "tasks.daily_practice.send_practice_reminder",
            "schedule": crontab(hour=9, minute=0),  # 9 AM daily
        },
        "weekly-progress-report": {
            "task": "tasks.progress_report.generate_weekly_report",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
        },
        "update-user-levels": {
            "task": "tasks.progress_report.update_student_levels",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        }
    }
)
```

### 4.2 Background Tasks

```python
# backend/tasks/daily_practice.py
from tasks import celery_app
from agents.exercise import ExerciseGeneratorAgent
from models import User, DailyPractice
import asyncio

@celery_app.task
def send_practice_reminder(user_id: int):
    """Send personalized daily practice"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    # Generate personalized exercises
    exercise_agent = ExerciseGeneratorAgent()
    exercises = asyncio.run(
        exercise_agent.generate_exercise_set(
            topic=user.current_focus_area,
            level=user.level,
            exercise_types=[ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_BLANK],
            quantity=5
        )
    )
    
    # Save to DB
    practice = DailyPractice(
        user_id=user_id,
        date=datetime.now().date(),
        exercises=exercises
    )
    db.add(practice)
    db.commit()
    
    # Send notification (email/push)
    send_notification(user.email, "Your daily practice is ready!", exercises)

@celery_app.task
def process_long_conversation(session_id: int):
    """Async processing of conversation for insights"""
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    # Analyze conversation
    grammar_agent = GrammarCheckerAgent()
    analysis = asyncio.run(
        grammar_agent.analyze_conversation(session.messages)
    )
    
    # Update session with insights
    session.grammar_insights = analysis
    db.commit()
```

### 4.3 Webhooks y Event Streaming

```python
# backend/api/webhooks.py
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

class ExerciseCompletedEvent(BaseModel):
    user_id: int
    exercise_id: int
    answers: List[dict]
    score: float
    completed_at: datetime

@router.post("/webhooks/exercise-completed")
async def handle_exercise_completion(
    event: ExerciseCompletedEvent,
    background_tasks: BackgroundTasks
):
    """Handle exercise completion event"""
    
    # Immediate response
    response = {"status": "received", "event_id": str(uuid.uuid4())}
    
    # Async processing
    background_tasks.add_task(process_exercise_completion, event)
    
    return response

async def process_exercise_completion(event: ExerciseCompletedEvent):
    # Update progress
    progress_agent = ProgressTrackerAgent()
    await progress_agent.track_session({
        "user_id": event.user_id,
        "activity": "exercise",
        "score": event.score,
        "timestamp": event.completed_at
    })
    
    # Check for level up
    if await should_level_up(event.user_id):
        await trigger_level_assessment(event.user_id)
    
    # Generate next recommendation
    await generate_next_practice(event.user_id)
```

---

## 🔍 Fase 5: Observabilidad y Monitoring (Semana 6)

### 5.1 LangSmith Integration

```python
# backend/config.py
from langsmith import Client
import os

langsmith_client = Client(
    api_key=os.getenv("LANGSMITH_API_KEY"),
    api_url="https://api.smith.langchain.com"
)

# En cada agente
from langsmith import traceable

class TutorAgent:
    @traceable(name="create_lesson", run_type="llm")
    async def create_lesson(self, topic: str, level: str):
        # Automáticamente trackeado en LangSmith
        pass
```

### 5.2 Métricas con Prometheus

```python
# backend/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Métricas
user_sessions = Counter('user_sessions_total', 'Total user sessions', ['user_id', 'session_type'])
response_time = Histogram('agent_response_seconds', 'Agent response time', ['agent_name'])
active_users = Gauge('active_users', 'Currently active users')
tokens_used = Counter('llm_tokens_total', 'Total LLM tokens used', ['model', 'agent'])
exercise_accuracy = Histogram('exercise_accuracy_percent', 'Exercise accuracy', ['level', 'type'])

# Uso en agentes
class TutorAgent:
    async def create_lesson(self, topic: str, level: str):
        with response_time.labels(agent_name='tutor').time():
            response = await self.llm.ainvoke(prompt)
            tokens_used.labels(model='claude-3.5', agent='tutor').inc(response.usage.total_tokens)
            return response
```

### 5.3 Dashboards Grafana

```yaml
# monitoring/grafana/dashboards/english-tutor.json
{
  "dashboard": {
    "title": "English Tutor AI - Overview",
    "panels": [
      {
        "title": "Active Users",
        "targets": [{"expr": "active_users"}]
      },
      {
        "title": "Response Time by Agent",
        "targets": [{"expr": "agent_response_seconds"}]
      },
      {
        "title": "Token Usage by Model",
        "targets": [{"expr": "rate(llm_tokens_total[5m])"}]
      },
      {
        "title": "Exercise Accuracy by Level",
        "targets": [{"expr": "exercise_accuracy_percent"}]
      }
    ]
  }
}
```

---

## 🚀 Fase 6: API y Frontend (Semana 7)

### 6.1 FastAPI Backend

```python
# backend/api/routes.py
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="English Tutor AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/evaluate")
async def start_evaluation(user_id: int):
    """Start level evaluation"""
    evaluator = EvaluatorAgent()
    result = await evaluator.graph.ainvoke({
        "messages": [],
        "student_level": None,
        "conversation_history": []
    })
    return result

@app.post("/api/v1/lesson/create")
async def create_lesson(request: LessonRequest):
    """Create personalized lesson"""
    tutor = TutorAgent(retriever)
    lesson = await tutor.create_lesson_with_rag(
        topic=request.topic,
        level=request.level
    )
    return lesson

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    """Real-time conversation"""
    await websocket.accept()
    conversation_agent = ConversationPartnerAgent()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            user_message = data["message"]
            
            # Process with agent
            response = await conversation_agent.chat(
                user_message=user_message,
                context={"level": data["level"], "topic": data.get("topic")}
            )
            
            # Send response
            await websocket.send_json({
                "reply": response["reply"],
                "corrections": response["corrections"],
                "new_vocabulary": response["new_vocabulary"]
            })
            
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")

@app.get("/api/v1/progress/{user_id}")
async def get_progress(user_id: int, period_days: int = 30):
    """Get progress report"""
    progress_agent = ProgressTrackerAgent(db)
    report = await progress_agent.generate_progress_report(user_id, period_days)
    return report
```

### 6.2 Frontend React/Next.js

```typescript
// frontend/src/app/chat/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    `ws://localhost:8000/ws/chat/${userId}`
  );

  useEffect(() => {
    if (lastMessage) {
      const response = JSON.parse(lastMessage.data);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.reply,
        corrections: response.corrections,
        vocabulary: response.new_vocabulary
      }]);
    }
  }, [lastMessage]);

  const handleSend = () => {
    sendMessage(JSON.stringify({
      message: input,
      level: userLevel,
      topic: currentTopic
    }));
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: input
    }]);
    
    setInput('');
  };

  return (
    <div className="chat-container">
      <MessageList messages={messages} />
      <ChatInput 
        value={input} 
        onChange={setInput} 
        onSend={handleSend}
        disabled={readyState !== WebSocket.OPEN}
      />
    </div>
  );
}
```

---

## ☁️ Fase 7: Deployment (Semana 8)

### 7.1 Kubernetes Deployment

```yaml
# k8s/deployments/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: english-tutor-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: english-tutor-backend
  template:
    metadata:
      labels:
        app: english-tutor-backend
    spec:
      containers:
      - name: backend
        image: your-registry/english-tutor-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: openai-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: postgres-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: english-tutor-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 7.2 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy English Tutor AI

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/
  
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t english-tutor-backend:${{ github.sha }} .
      
      - name: Push to registry
        run: docker push your-registry/english-tutor-backend:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/english-tutor-backend \
            backend=your-registry/english-tutor-backend:${{ github.sha }}
```

---

## 📊 Evaluación del Proyecto Final

### Checklist de Completitud (100 puntos)

#### ✅ Multi-Model Support (15 pts)
- [ ] OpenAI integration (GPT-4)
- [ ] Anthropic integration (Claude)
- [ ] Fallback logic entre modelos
- [ ] Cost tracking por modelo

#### ✅ RAG Implementation (15 pts)
- [ ] Vector database configurada
- [ ] Contenido educativo vectorizado
- [ ] Hybrid search implementado
- [ ] Re-ranking activo

#### ✅ Multi-Agent Architecture (20 pts)
- [ ] 6 agentes especializados funcionando
- [ ] LangGraph supervisor
- [ ] State management robusto
- [ ] Inter-agent communication

#### ✅ Event-Driven Components (15 pts)
- [ ] Celery workers activos
- [ ] Scheduled tasks funcionando
- [ ] Webhooks implementados
- [ ] Message queue operacional

#### ✅ Observability Stack (15 pts)
- [ ] LangSmith tracing
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Alerting configurado

#### ✅ Production-Ready (15 pts)
- [ ] Docker containers
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Load testing completado

#### ✅ Documentation (5 pts)
- [ ] Architecture diagram
- [ ] API docs (Swagger)
- [ ] Deployment guide
- [ ] Runbook

---

## 📚 Recursos y Referencias

### Repositorios de Referencia
- [LangGraph Multi-Agent](https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent)
- [Educational Chatbot](https://github.com/langchain-ai/langchain/tree/master/templates/educational-chatbot)
- [RAG Advanced](https://github.com/langchain-ai/rag-from-scratch)

### Datasets para Contenido
- [English Grammar Lessons](https://github.com/topics/english-grammar)
- [Vocabulary Lists by CEFR](https://github.com/hermitdave/FrequencyWords)
- [English Exercises](https://github.com/topics/english-learning)

### Herramientas Recomendadas
- **Development:** VS Code + Cursor AI
- **Testing:** Pytest + Postman
- **Cloud:** AWS EKS / GCP GKE
- **Monitoring:** DataDog / New Relic
- **Error Tracking:** Sentry

---

## 🎯 Próximos Pasos

1. **Semana 1-2:** Setup completo + Agentes básicos
2. **Semana 3-4:** RAG system + Integration
3. **Semana 5-6:** Event-driven + Observability
4. **Semana 7:** Frontend + API polish
5. **Semana 8:** Deployment + Testing
6. **Semana 9-10:** Optimización + Documentation

**¡Comienza tu proyecto ahora! 🚀**