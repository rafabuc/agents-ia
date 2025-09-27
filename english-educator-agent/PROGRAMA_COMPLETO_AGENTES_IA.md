# Programa de Aprendizaje: Desarrollo de Agentes de IA con Python

## 📋 Información del Curso
**Duración estimada:** 8-10 semanas  
**Nivel:** Intermedio-Avanzado (requiere experiencia en Python y desarrollo web)  
**Requisitos previos:** Python, APIs REST, programación asíncrona

---

## 🧪 Resumen de Laboratorios

### Total de Labs: 35+ ejercicios prácticos

| Módulo | # Labs | Enfoque Principal | Herramientas Clave |
|--------|--------|-------------------|-------------------|
| 1. Fundamentos | 3 | APIs, ReAct, Memory | OpenAI, Anthropic, Local |
| 2. LangChain | 4 | Chains, Tools, Memory | LangChain, APIs, Local |
| 3. LangGraph | 6 | Grafos, Multi-agente, HITL | LangGraph, Docker, Cloud |
| 4. RAG | 6 | Embeddings, Vector DBs, Optimización | Pinecone, Chroma, Cloud |
| 5. Event-Driven | 5 | Webhooks, Queues, Workers | RabbitMQ, Celery, Kafka |
| 6. Frameworks | 5 | CrewAI, AutoGen, LlamaIndex | Multiple frameworks, Docker |
| 7. Herramientas | 6 | Observabilidad, Evaluación | LangSmith, Phoenix, Grafana |
| 8. Proyectos Finales | 5 | Sistemas completos | Full stack, K8s, Cloud |

### Progresión de Complejidad:
```
Local → Docker → Docker Compose → Cloud → Kubernetes
```

### Entornos Recomendados por Fase:

**Fase 1 (Semanas 1-2):** Local development
- Python + venv
- Jupyter Notebooks
- APIs locales

**Fase 2 (Semanas 3-4):** Docker local
- Docker Desktop
- Docker Compose
- Servicios containerizados

**Fase 3 (Semanas 5-6):** Cloud básico
- Render/Railway (backend)
- Vercel (frontend)
- Managed databases

**Fase 4 (Semanas 7-10):** Cloud producción
- AWS/GCP/Azure
- Kubernetes
- Monitoring completo

---

## Módulo 1: Fundamentos de LLMs y Agentes de IA

### 1.1 Introducción a Large Language Models
- Conceptos básicos de LLMs (GPT-4, Claude, etc.)
- APIs de OpenAI y Anthropic
- Tokens, contexto y limitaciones
- Prompting efectivo y prompt engineering

**Práctica:**
- Configuración de entornos con OpenAI y Anthropic
- Primeros prompts y experimentación con temperatura/top_p

**Referencias:**
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

**Repositorios:**
- [openai-cookbook](https://github.com/openai/openai-cookbook)
- [anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook)

### 🧪 Laboratorios Módulo 1

**Lab 1.1: Configuración de Entorno Base**
- Configurar API keys de OpenAI y Anthropic
- Crear primer chat completion
- Experimentar con parámetros (temperature, max_tokens, top_p)

**Herramientas:**
- Python 3.9+, venv o conda
- Jupyter Notebook / VS Code
- Variables de entorno (.env con python-dotenv)

**Repositorio de referencia:**
- [llm-basics-tutorial](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb)

**Lab 1.2: Construcción de Agente ReAct Simple**
- Implementar ciclo Think → Act → Observe
- Crear herramienta de cálculo básica
- Logging de razonamiento del agente

**Herramientas:**
- Python, OpenAI API
- Local development

**Repositorio de referencia:**
- [react-agent-scratch](https://github.com/langchain-ai/langchain/blob/master/cookbook/react_agent_from_scratch.ipynb)

### 1.2 Conceptos de Agentes de IA
- Definición y tipos de agentes (ReAct, Plan-and-Execute, etc.)
- Diferencia entre chatbots y agentes autónomos
- Ciclo de razonamiento: Observación → Pensamiento → Acción
- Memory y gestión de estado

**Referencias:**
- [LangChain Agents Concepts](https://python.langchain.com/docs/modules/agents/)
- Paper: "ReAct: Synergizing Reasoning and Acting in Language Models"

### 🧪 Laboratorios Módulo 1 (Continuación)

**Lab 1.3: Sistema de Memoria para Conversaciones**
- Implementar buffer memory
- Crear conversación multi-turn
- Implementar summary memory para conversaciones largas

**Herramientas:**
- Python, dict/JSON para persistencia
- Optional: Redis para memoria distribuida

**Repositorio de referencia:**
- [memory-examples](https://github.com/langchain-ai/langchain/tree/master/cookbook)

---

## Módulo 2: LangChain - Framework Base

### 2.1 Fundamentos de LangChain
- Arquitectura de LangChain
- Chains, Prompts y Output Parsers
- LLM wrappers y abstracción de modelos
- Memory systems (ConversationBufferMemory, ConversationSummaryMemory)

**Práctica:**
- Creación de chains básicas
- Implementación de conversaciones con memoria

**Referencias:**
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/)

**Repositorios:**
- [langchain](https://github.com/langchain-ai/langchain)
- [langchain-examples](https://github.com/gkamradt/langchain-tutorials)

### 2.2 Tools y Tool Calling
- Function calling con OpenAI y Anthropic
- Creación de herramientas personalizadas
- Tool execution y error handling
- Integración con APIs externas

**Práctica:**
- Desarrollo de agente con herramientas custom
- Integración con APIs de terceros (weather, search, etc.)

**Repositorios:**
- [langchain-tools-examples](https://github.com/langchain-ai/langchain/tree/master/libs/langchain/langchain/tools)

### 🧪 Laboratorios Módulo 2

**Lab 2.1: Pipeline LCEL Completo**
- Crear chain con prompt → LLM → parser
- Implementar streaming de respuestas
- Agregar fallbacks y error handling

**Herramientas:**
- Local: Python, LangChain
- Cloud: LangSmith para tracing (opcional)

**Repositorio de referencia:**
- [lcel-examples](https://github.com/langchain-ai/langchain/tree/master/cookbook)

**Lab 2.2: Memory Systems Comparativo**
- Implementar ConversationBufferMemory
- Implementar ConversationSummaryMemory
- Comparar uso de tokens y calidad

**Herramientas:**
- Jupyter Notebook
- Gráficas con matplotlib para comparación

**Repositorio de referencia:**
- [memory-types](https://github.com/langchain-ai/langchain/blob/master/cookbook/memory_in_agent.ipynb)

**Lab 2.3: Agente con Herramientas Personalizadas**
- Crear herramienta de web scraping
- Crear herramienta de búsqueda en API
- Integrar con agente ReAct

**Herramientas:**
- Beautiful Soup / Playwright para scraping
- Requests para APIs
- Local development

**Repositorio de referencia:**
- [custom-tools-agent](https://github.com/langchain-ai/langchain/blob/master/cookbook/custom_agent_with_plugin_retrieval.ipynb)

**Lab 2.4: Function Calling Multi-Tool**
- Implementar 5+ herramientas (calculadora, weather, search, etc.)
- Parallel function calling
- Error handling robusto

**Herramientas:**
- APIs: OpenWeatherMap, SerpAPI
- Local o Docker para desarrollo

**Repositorio de referencia:**
- [function-calling-examples](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb)

---

## Módulo 3: LangGraph - Orquestación Avanzada

### 3.1 Introducción a LangGraph
- Grafos de estado (StateGraph)
- Nodos, aristas y flujos condicionales
- Persistencia y checkpointing
- Diferencias con LangChain clásico

**Práctica:**
- Primer agente con LangGraph
- Implementación de flujos condicionales

**Referencias:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Conceptual Guide](https://langchain-ai.github.io/langgraph/concepts/)

**Repositorios:**
- [langgraph](https://github.com/langchain-ai/langgraph)
- [langgraph-examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

### 3.2 Arquitecturas de Agentes con LangGraph
- **ReAct Agent**: Razonamiento + Acción
- **Plan-and-Execute Agent**: Planificación estratégica
- **Multi-Agent Systems**: Colaboración entre agentes
- **Human-in-the-Loop**: Aprobación humana en flujos

**Práctica:**
- Implementación de cada tipo de arquitectura
- Sistema multi-agente con roles específicos

**Repositorios:**
- [langgraph-agent-architectures](https://github.com/langchain-ai/langgraph/tree/main/examples/agent_executor)

### 🧪 Laboratorios Módulo 3

**Lab 3.1: Primer Grafo de Estado con LangGraph**
- Crear StateGraph básico
- Implementar nodos y edges condicionales
- Visualizar el grafo

**Herramientas:**
- LangGraph, graphviz para visualización
- Local development

**Repositorio de referencia:**
- [langgraph-quickstart](https://github.com/langchain-ai/langgraph/blob/main/examples/chat_agent_executor_with_function_calling/base.ipynb)

**Lab 3.2: Agente ReAct con LangGraph**
- Implementar agent_scratchpad
- Tools execution con error recovery
- Checkpointing para persistencia

**Herramientas:**
- LangGraph, SQLite para checkpoints
- Local o Railway/Render para deployment

**Repositorio de referencia:**
- [react-agent-langgraph](https://github.com/langchain-ai/langgraph/tree/main/examples/react-agent)

**Lab 3.3: Plan-and-Execute Agent**
- Nodo planner que crea pasos
- Nodo executor que ejecuta tareas
- Replanning dinámico

**Herramientas:**
- LangGraph + GPT-4 (mejor para planning)
- Docker para entorno aislado

**Repositorio de referencia:**
- [plan-execute](https://github.com/langchain-ai/langgraph/tree/main/examples/plan-and-execute)

**Lab 3.4: Sistema Multi-Agente Colaborativo**
- 3+ agentes especializados (researcher, writer, critic)
- Comunicación entre agentes
- Supervisor para routing

**Herramientas:**
- LangGraph, PostgreSQL para estado compartido
- Docker Compose para orquestación

**Repositorio de referencia:**
- [multi-agent-collaboration](https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent)
- [hierarchical-teams](https://github.com/langchain-ai/langgraph/tree/main/examples/hierarchical_agent_teams)

**Lab 3.5: Human-in-the-Loop Workflow**
- Interrupt points para aprobación
- Resume después de input humano
- Audit trail completo

**Herramientas:**
- LangGraph + FastAPI para endpoints
- Frontend simple (Streamlit/Gradio)
- Redis para estado temporal

**Repositorio de referencia:**
- [human-in-loop](https://github.com/langchain-ai/langgraph/blob/main/examples/human-in-the-loop.ipynb)

**Lab 3.6: Streaming y Observabilidad**
- Streaming de tokens en real-time
- Integración con LangSmith
- Dashboard de métricas

**Herramientas:**
- LangGraph + Server-Sent Events
- LangSmith (cuenta gratuita)
- Cloud: Vercel/Netlify para frontend

**Repositorio de referencia:**
- [streaming-examples](https://github.com/langchain-ai/langgraph/tree/main/examples/streaming)

### 3.3 Orquestación Avanzada
- Supervisión y routing entre agentes
- Manejo de errores y reintentos
- Streaming de respuestas
- Debugging y observabilidad (LangSmith)

**Práctica:**
- Sistema de agentes con supervisor
- Implementación de fallbacks y recovery

---

## Módulo 4: Retrieval Augmented Generation (RAG)

### 4.1 Fundamentos de RAG
- ¿Qué es RAG y cuándo usarlo?
- Embeddings y bases de datos vectoriales
- Chunking strategies y document loaders
- Similarity search y semantic search

**Práctica:**
- Implementación básica de RAG
- Comparación de estrategias de chunking

**Referencias:**
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

**Repositorios:**
- [rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch)

### 🧪 Laboratorios Módulo 4

**Lab 4.1: RAG Básico desde Cero**
- Cargar documentos PDF/TXT
- Crear embeddings con OpenAI
- Implementar similarity search
- Q&A sobre documentos

**Herramientas:**
- LangChain, FAISS (local)
- PyPDF2 para PDFs
- Local development

**Repositorio de referencia:**
- [rag-tutorial-basic](https://github.com/langchain-ai/rag-from-scratch)
- [pdf-qa-example](https://github.com/langchain-ai/langchain/blob/master/cookbook/retrieval_qa_with_sources.ipynb)

**Lab 4.2: Chunking Strategies Comparison**
- Fixed-size chunking
- Semantic chunking
- Recursive character splitting
- Medir accuracy por estrategia

**Herramientas:**
- Python notebooks
- Métricas: Rouge, BLEU
- Local development

**Repositorio de referencia:**
- [chunking-strategies](https://github.com/FullStackRetrieval-com/RetrievalTutorials/tree/main/tutorials/LevelsOfTextSplitting)

**Lab 4.3: Vector Stores Benchmark**
- Implementar con Chroma, Pinecone, Qdrant
- Comparar velocidad y accuracy
- Medir costos

**Herramientas:**
- Docker para Qdrant local
- Pinecone free tier
- ChromaDB local
- Grafana para visualización

**Repositorio de referencia:**
- [vector-db-comparison](https://github.com/langchain-ai/langchain/tree/master/docs/docs/integrations/vectorstores)

**Lab 4.4: RAG Avanzado - Multi-Query**
- Query expansion automática
- Parallel retrieval
- Result fusion

**Herramientas:**
- LangChain MultiQueryRetriever
- Redis para caching
- Local o Fly.io para deployment

**Repositorio de referencia:**
- [multi-query-rag](https://github.com/langchain-ai/langchain/blob/master/cookbook/multi_query_retriever.ipynb)

**Lab 4.5: Corrective RAG (CRAG)**
- Evaluación de relevancia
- Web search fallback
- Self-correction loop

**Herramientas:**
- LangGraph para flow
- Tavily/SerpAPI para web search
- Docker compose

**Repositorio de referencia:**
- [corrective-rag](https://github.com/langchain-ai/langgraph/tree/main/examples/rag/langgraph_crag.ipynb)

**Lab 4.6: Production RAG System**
- Pipeline completo con monitoring
- Hybrid search (dense + sparse)
- Re-ranking con cross-encoders
- Cache layer con Redis

**Herramientas:**
- Docker Compose (Qdrant + Redis)
- Elasticsearch para sparse search
- Cloud: AWS/GCP para deployment
- Prometheus + Grafana para monitoring

**Repositorio de referencia:**
- [production-rag](https://github.com/ray-project/llm-applications/tree/main/rag)
- [hybrid-search-example](https://github.com/langchain-ai/langchain/blob/master/cookbook/hybrid_search.ipynb)

### 4.2 Vector Stores y Bases de Datos
- **Pinecone**: Cloud vector database
- **Chroma**: Embedded vector DB
- **Weaviate**: Open-source vector search
- **FAISS**: Facebook AI Similarity Search
- **Qdrant**: Vector search engine

**Práctica:**
- Implementación con múltiples vector stores
- Benchmark de performance

**Referencias:**
- [Pinecone Docs](https://docs.pinecone.io/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Weaviate Docs](https://weaviate.io/developers/weaviate)

**Repositorios:**
- [chromadb](https://github.com/chroma-core/chroma)
- [qdrant](https://github.com/qdrant/qdrant)

### 4.3 RAG Avanzado
- Multi-query retrieval
- Self-query retrieval
- Contextual compression
- Re-ranking y hybrid search
- RAPTOR (Recursive Abstractive Processing)
- Corrective RAG (CRAG)

**Práctica:**
- Implementación de técnicas avanzadas
- Optimización de retrieval accuracy

**Referencias:**
- [Advanced RAG Techniques](https://python.langchain.com/docs/use_cases/question_answering/)
- Paper: "RAPTOR: Recursive Abstractive Processing"

---

## Módulo 5: Arquitecturas Event-Driven

### 5.1 Sistemas Basados en Eventos
- Arquitectura event-driven vs request-response
- Webhooks y callbacks
- Message queues (RabbitMQ, Redis Streams)
- Event streaming con Kafka

**Práctica:**
- Agente reactivo a eventos externos
- Integración con webhooks

**Referencias:**
- [Event-Driven Architecture Guide](https://martinfowler.com/articles/201701-event-driven.html)

### 5.2 Agentes Reactivos
- Triggers y event handlers
- Scheduling y tareas programadas
- Background workers con Celery
- Real-time notifications

**Práctica:**
- Sistema de alertas con agentes
- Procesamiento asíncrono de eventos

**Repositorios:**
- [celery](https://github.com/celery/celery)
- [redis](https://github.com/redis/redis-py)

### 🧪 Laboratorios Módulo 5

**Lab 5.1: Sistema de Webhooks**
- Crear endpoint FastAPI para recibir eventos
- Procesar eventos con agente
- Responder con webhooks salientes

**Herramientas:**
- FastAPI + ngrok para desarrollo local
- PostgreSQL para event store
- Cloud: Railway/Render

**Repositorio de referencia:**
- [fastapi-webhooks](https://github.com/tiangolo/fastapi/tree/master/docs_src/events)

**Lab 5.2: Message Queue con RabbitMQ**
- Producer: publicar tareas
- Consumer: agente procesa mensajes
- Dead letter queue para errores

**Herramientas:**
- Docker (RabbitMQ)
- Pika (Python client)
- Local development

**Repositorio de referencia:**
- [rabbitmq-agent-example](https://github.com/rabbitmq/rabbitmq-tutorials/tree/main/python)

**Lab 5.3: Background Workers con Celery**
- Tasks asíncronas con agentes
- Scheduled tasks (cron-like)
- Task chaining y workflows

**Herramientas:**
- Celery + Redis/RabbitMQ
- Flower para monitoring
- Docker Compose

**Repositorio de referencia:**
- [celery-langchain](https://github.com/langchain-ai/langchain/discussions/8849)
- [celery-examples](https://github.com/celery/celery/tree/main/examples)

**Lab 5.4: Sistema de Alertas Inteligente**
- Monitor de eventos (logs, métricas)
- Agente analiza y decide alertas
- Notificaciones multi-canal (Slack, Email)

**Herramientas:**
- Redis Streams para eventos
- Slack SDK / SendGrid
- Docker + Kubernetes (optional)

**Repositorio de referencia:**
- [intelligent-alerting](https://github.com/Netflix/dispatch)

**Lab 5.5: Event-Driven RAG**
- Nuevo documento → auto-indexing
- Query events → async retrieval
- Update events → re-embedding

**Herramientas:**
- Kafka o Redis Streams
- Vector DB con webhooks
- Cloud: Confluent Cloud (Kafka managed)

**Repositorio de referencia:**
- [event-driven-architecture](https://github.com/wmo-raf/nmhs-cms)

---

## Módulo 6: Frameworks Alternativos y Especializados

### 6.1 CrewAI
- Role-based agent system
- Tareas colaborativas
- Process flows (sequential, hierarchical)

**Referencias:**
- [CrewAI Documentation](https://docs.crewai.com/)

**Repositorios:**
- [crewAI](https://github.com/joaomdmoura/crewAI)

### 6.2 AutoGen (Microsoft)
- Conversational agents
- Group chat y multi-agent collaboration
- Code execution y validation

**Referencias:**
- [AutoGen Documentation](https://microsoft.github.io/autogen/)

**Repositorios:**
- [autogen](https://github.com/microsoft/autogen)

### 6.3 LlamaIndex
- Especializado en RAG y data indexing
- Query engines avanzados
- Integration con LangChain

**Referencias:**
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)

**Repositorios:**
- [llama_index](https://github.com/run-llama/llama_index)

### 6.4 Semantic Kernel (Microsoft)
- SDK enterprise-grade
- Planners y plugins
- Memory y connectors

**Referencias:**
- [Semantic Kernel Docs](https://learn.microsoft.com/en-us/semantic-kernel/)

**Repositorios:**
- [semantic-kernel](https://github.com/microsoft/semantic-kernel)

### 🧪 Laboratorios Módulo 6

**Lab 6.1: CrewAI - Equipo de Marketing**
- 3 agentes: Researcher, Writer, Editor
- Process: Sequential workflow
- Output: Blog post completo

**Herramientas:**
- CrewAI framework
- Local development
- Optional: Streamlit para UI

**Repositorio de referencia:**
- [crewai-examples](https://github.com/joaomdmoura/crewAI-examples)
- [marketing-crew](https://github.com/joaomdmoura/crewAI-examples/tree/main/marketing_strategy)

**Lab 6.2: AutoGen - Code Review System**
- Assistant agent + User proxy
- Code execution en sandbox
- Iterative debugging

**Herramientas:**
- AutoGen, Docker para code execution
- Local development

**Repositorio de referencia:**
- [autogen-code-examples](https://github.com/microsoft/autogen/tree/main/notebook)
- [code-execution](https://github.com/microsoft/autogen/blob/main/notebook/agentchat_code_execution.ipynb)

**Lab 6.3: LlamaIndex - Advanced RAG**
- Query engines con metadata filtering
- Sub-question query engine
- Comparar con LangChain RAG

**Herramientas:**
- LlamaIndex, Vector DB
- Local development

**Repositorio de referencia:**
- [llamaindex-examples](https://github.com/run-llama/llama_index/tree/main/docs/docs/examples)
- [sub-question-engine](https://github.com/run-llama/llama_index/blob/main/docs/docs/examples/query_engine/sub_question_query_engine.ipynb)

**Lab 6.4: Semantic Kernel - Plugin System**
- Crear plugins reutilizables
- Planner automático
- Memory connectors

**Herramientas:**
- .NET o Python SK
- Local development

**Repositorio de referencia:**
- [semantic-kernel-samples](https://github.com/microsoft/semantic-kernel/tree/main/python/samples)

**Lab 6.5: Frameworks Comparison Project**
- Mismo caso de uso en 3 frameworks
- Benchmark: velocidad, tokens, código
- Documentar pros/cons

**Herramientas:**
- LangGraph + CrewAI + AutoGen
- Jupyter Notebook para análisis
- Local development

---

## Módulo 7: Herramientas Complementarias

### 7.1 Observabilidad y Debugging
- **LangSmith**: Tracing y monitoring
- **Weights & Biases**: Experiment tracking
- **Phoenix**: Open-source observability
- Logging estructurado y métricas

**Práctica:**
- Implementación de tracing end-to-end
- Dashboard de métricas

**Referencias:**
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Phoenix by Arize](https://docs.arize.com/phoenix)

**Repositorios:**
- [phoenix](https://github.com/Arize-ai/phoenix)

### 7.2 Evaluación de Agentes
- Benchmarks y test suites
- Evaluación con LLMs (LLM-as-judge)
- Métricas específicas (accuracy, latency, cost)
- A/B testing de prompts

**Práctica:**
- Framework de evaluación automatizada
- Optimización basada en métricas

**Referencias:**
- [LangChain Evaluation](https://python.langchain.com/docs/guides/evaluation/)
- [OpenAI Evals](https://github.com/openai/evals)

**Repositorios:**
- [evals](https://github.com/openai/evals)

### 7.3 Optimización y Producción
- Caching de respuestas (Redis, GPTCache)
- Rate limiting y quota management
- Fallbacks entre modelos
- Cost optimization strategies

**Práctica:**
- Sistema de producción con caching
- Monitoring de costos

**Repositorios:**
- [gptcache](https://github.com/zilliztech/GPTCache)

### 🧪 Laboratorios Módulo 7

**Lab 7.1: Tracing Completo con LangSmith**
- Configurar proyecto en LangSmith
- Tracing de chains completas
- Debugging de fallos
- Playground para iteración

**Herramientas:**
- LangSmith (cuenta free tier)
- LangChain con callbacks
- Local development

**Repositorio de referencia:**
- [langsmith-cookbook](https://github.com/langchain-ai/langsmith-cookbook)

**Lab 7.2: Open-Source Observability**
- Phoenix tracing setup
- OpenTelemetry integration
- Dashboard personalizado

**Herramientas:**
- Phoenix Arize (Docker)
- Prometheus + Grafana
- Local o cloud deployment

**Repositorio de referencia:**
- [phoenix-examples](https://github.com/Arize-ai/phoenix/tree/main/tutorials)
- [opentelemetry-langchain](https://github.com/Arize-ai/openinference)

**Lab 7.3: Sistema de Evaluación Automatizada**
- Test suite con casos gold standard
- LLM-as-judge evaluation
- Regression testing

**Herramientas:**
- pytest + LangChain evaluation
- OpenAI Evals
- CI/CD: GitHub Actions

**Repositorio de referencia:**
- [langchain-evaluations](https://github.com/langchain-ai/langchain/tree/master/libs/langchain/langchain/evaluation)
- [openai-evals](https://github.com/openai/evals)

**Lab 7.4: Métricas y Benchmarking**
- Accuracy, precision, recall
- Latency y throughput
- Cost per query
- Dashboard en tiempo real

**Herramientas:**
- Custom metrics con Python
- TimescaleDB para time-series
- Grafana para visualización
- Cloud: AWS CloudWatch / GCP Monitoring

**Repositorio de referencia:**
- [llm-benchmarking](https://github.com/explodinggradients/ragas)

**Lab 7.5: Caching y Optimización**
- Semantic caching con GPTCache
- Redis para response cache
- Medir ahorro de costos

**Herramientas:**
- GPTCache + Redis
- Docker Compose
- Local development

**Repositorio de referencia:**
- [gptcache-examples](https://github.com/zilliztech/GPTCache/tree/main/examples)

**Lab 7.6: Production Monitoring Stack**
- Logging estructurado (JSON)
- Distributed tracing (Jaeger)
- Alerting (PagerDuty/Slack)
- Cost tracking

**Herramientas:**
- ELK Stack o Loki
- Jaeger para tracing
- Prometheus + AlertManager
- Cloud: ECS/GKE para deployment

**Repositorio de referencia:**
- [llm-monitoring](https://github.com/whylabs/langkit)

---

## Módulo 8: Casos de Uso y Proyectos Finales

### 8.1 Patrones de Diseño Comunes
- **Customer Support Agent**: RAG + function calling
- **Research Assistant**: Multi-step reasoning
- **Code Assistant**: Execution + validation
- **Data Analysis Agent**: SQL + visualization
- **Personal Assistant**: Calendar + email + tasks

### 8.2 Proyecto Final Integrador
Desarrollar un sistema multi-agente que integre:
- Múltiples modelos (GPT-4, Claude)
- RAG con vector database
- Arquitectura event-driven
- Observabilidad completa
- Deployment production-ready

**Ejemplos de Proyectos:**
1. Sistema de análisis de documentos empresariales
2. Asistente de investigación académica
3. Plataforma de automatización de workflows
4. Sistema de atención al cliente inteligente

### 🧪 Laboratorios Módulo 8

**Lab 8.1: Customer Support Agent (Completo)**
- RAG sobre knowledge base
- Ticket creation con tools
- Sentiment analysis
- Human handoff cuando necesario
- Metrics dashboard

**Herramientas:**
- LangGraph + RAG
- PostgreSQL + Vector DB
- Slack/Zendesk integration
- Cloud: AWS/GCP full stack
- Monitoring: DataDog/New Relic

**Stack completo:**
```
Frontend: Streamlit/React
Backend: FastAPI
Agent: LangGraph
DB: PostgreSQL + Qdrant
Cache: Redis
Queue: Celery + RabbitMQ
Monitoring: LangSmith + Grafana
```

**Repositorio de referencia:**
- [customer-support-bot](https://github.com/langchain-ai/langchain/tree/master/templates/customer-support)

**Lab 8.2: Research Assistant (Academic)**
- Multi-source RAG (PDFs, arXiv, web)
- Citation tracking
- Summary generation
- Report writing con LaTeX output

**Herramientas:**
- LlamaIndex para scholarly data
- ArXiv API + Semantic Scholar
- MongoDB para paper storage
- Cloud: Vercel + Supabase

**Stack:**
```
Frontend: Next.js
Backend: FastAPI
Agent: LlamaIndex + LangGraph
Search: Elasticsearch
Storage: MongoDB + S3
```

**Repositorio de referencia:**
- [research-assistant](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/readers/llama-index-readers-papers)

**Lab 8.3: Code Assistant con Sandbox**
- Code generation multi-lenguaje
- Safe execution en Docker
- Test generation automático
- GitHub integration

**Herramientas:**
- AutoGen para code execution
- Docker API para sandboxing
- GitHub Actions para CI/CD
- Cloud: Fly.io para containers

**Stack:**
```
IDE Extension: VS Code plugin
Backend: FastAPI + WebSocket
Agent: AutoGen + GPT-4
Execution: Docker containers
Storage: PostgreSQL
```

**Repositorio de referencia:**
- [code-assistant](https://github.com/microsoft/autogen/tree/main/notebook)
- [safe-code-execution](https://github.com/e2b-dev/e2b)

**Lab 8.4: Data Analysis Agent**
- Natural language → SQL
- Data visualization automática
- Insights generation
- Report scheduling

**Herramientas:**
- LangChain SQL chains
- Plotly/Matplotlib para viz
- DuckDB o PostgreSQL
- Cloud: Snowflake/BigQuery integration

**Stack:**
```
UI: Streamlit
Backend: FastAPI
Agent: LangChain + Claude
DB: PostgreSQL/Snowflake
Cache: Redis
Scheduler: Airflow/Prefect
```

**Repositorio de referencia:**
- [sql-agent](https://github.com/langchain-ai/langchain/tree/master/templates/sql-llama2)
- [data-analysis-agent](https://github.com/langchain-ai/langchain/blob/master/cookbook/sql_db_qa.ipynb)

**Lab 8.5: Multi-Agent Workflow Platform**
- Visual workflow builder
- Library de agentes pre-built
- Event-driven execution
- Monitoring y alerting completo

**Herramientas:**
- LangGraph para workflows
- React Flow para UI
- Temporal.io para orchestration
- Cloud: Kubernetes deployment

**Stack completo:**
```
Frontend: React + React Flow
Backend: FastAPI + GraphQL
Orchestration: Temporal.io
Agents: LangGraph multi-agent
Storage: PostgreSQL + Redis
Queue: Kafka
Monitoring: Prometheus + Grafana
Tracing: Jaeger
```

**Repositorio de referencia:**
- [workflow-automation](https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent)
- [n8n-ai-alternative](https://github.com/n8n-io/n8n)

---

## 🛠️ Setup de Ambiente Recomendado

### Desarrollo Local
```bash
# Core Python
Python 3.10+
pip install langchain langgraph langchain-openai langchain-anthropic
pip install chromadb pinecone-client qdrant-client
pip install fastapi uvicorn celery redis

# Notebooks y desarrollo
pip install jupyter ipykernel
pip install python-dotenv

# Observabilidad
pip install langsmith phoenix-ai
pip install prometheus-client

# Testing
pip install pytest pytest-asyncio
```

### Docker Compose Básico
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports: ["6379:6379"]
  
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    ports: ["5432:5432"]
```

### Cloud Providers Recomendados

**Para Desarrollo/Testing:**
- **Replit**: Prototipado rápido
- **Google Colab**: Notebooks gratuitos
- **Render/Railway**: Backend deployment free tier
- **Vercel**: Frontend deployment
- **Supabase**: PostgreSQL + storage gratuito

**Para Producción:**
- **AWS**: ECS/EKS + Lambda + RDS
- **GCP**: Cloud Run + GKE + Vertex AI
- **Azure**: Container Apps + AKS + OpenAI Service
- **Fly.io**: Global deployment

### Vector Databases Cloud
- **Pinecone**: Free tier 1GB
- **Weaviate Cloud**: Free tier disponible
- **Qdrant Cloud**: Free tier 1GB
- **Zilliz Cloud**: Managed Milvus

### Monitoring Services
- **LangSmith**: 5000 traces/month gratis
- **DataDog**: 14-day trial
- **New Relic**: Free tier
- **Grafana Cloud**: Free tier

---

## 📊 Estructura de Entrega de Labs

Cada laboratorio debe incluir:

1. **README.md** con:
   - Objetivo del lab
   - Prerequisites
   - Setup instructions
   - Paso a paso
   - Expected outputs

2. **requirements.txt** o **pyproject.toml**

3. **docker-compose.yml** si aplica

4. **.env.example** con variables necesarias

5. **tests/** directorio con unit tests

6. **notebooks/** si incluye Jupyter

7. **LEARNINGS.md**: Documentar problemas y soluciones

---

## 📝 Sistema de Evaluación de Labs

### Criterios (100 puntos total):
- **Funcionalidad (40 pts)**: El agente cumple el objetivo
- **Código limpio (20 pts)**: Best practices, typing, docstrings
- **Error handling (15 pts)**: Manejo robusto de errores
- **Documentación (15 pts)**: README claro y completo
- **Testing (10 pts)**: Unit tests y coverage

### Entregables:
- Repositorio GitHub por laboratorio
- Demo en video (5 min) explicando funcionamiento
- Post-mortem con learnings

---

## 🎓 Proyecto Final - Requisitos Mínimos

El proyecto final debe incluir **TODOS** estos componentes:

### 1. **Multi-Model Support**
- Al menos 2 proveedores (OpenAI + Anthropic/Local)
- Fallback automático entre modelos

### 2. **RAG Implementation**
- Vector database en producción
- Técnica avanzada (CRAG o Multi-Query)
- Hybrid search

### 3. **Multi-Agent Architecture**
- Mínimo 3 agentes especializados
- Orquestación con LangGraph
- State management robusto

### 4. **Event-Driven Component**
- Queue o streaming system
- Background workers
- Webhooks o scheduled tasks

### 5. **Observability Stack**
- Distributed tracing
- Metrics dashboard
- Alerting system
- Cost tracking

### 6. **Production-Ready**
- Docker/Kubernetes deployment
- CI/CD pipeline
- Load testing results
- Security audit

### 7. **Documentation**
- Architecture diagram
- API documentation (OpenAPI)
- Deployment guide
- Runbook operacional

### Evaluación Final: 
**Presentación 30 min + Q&A + Code review**

---

## 📚 Recursos Adicionales

### Libros Recomendados
- "Build a Large Language Model (From Scratch)" - Sebastian Raschka
- "Designing Large Language Model Applications" - O'Reilly

### Cursos Online
- [DeepLearning.AI - LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/)
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/)
- [DeepLearning.AI - Building Multi-Agent Systems](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)

### Comunidades
- [LangChain Discord](https://discord.gg/langchain)
- [r/LangChain Reddit](https://www.reddit.com/r/LangChain/)
- [AI Engineer Community](https://www.latent.space/community)

### Repositorios de Referencia Completos
- [langchain-ai/langchain](https://github.com/langchain-ai/langchain) - Framework principal
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) - Orquestación con grafos
- [microsoft/autogen](https://github.com/microsoft/autogen) - Multi-agent framework
- [joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI) - Role-based agents
- [run-llama/llama_index](https://github.com/run-llama/llama_index) - Data framework
- [openai/openai-cookbook](https://github.com/openai/openai-cookbook) - Ejemplos OpenAI
- [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) - Ejemplos Claude
- [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Autonomous agent
- [mendableai/firecrawl](https://github.com/mendableai/firecrawl) - Web scraping para RAG
- [build-with-ai/agentic-workflow](https://github.com/langchain-ai/agentic-workflow-patterns) - Patrones de workflows

---

## 🎯 Metodología de Aprendizaje

### Semana a Semana
- **Semanas 1-2:** Módulos 1-2 (Fundamentos + LangChain)
- **Semanas 3-4:** Módulo 3 (LangGraph)
- **Semanas 5-6:** Módulos 4-5 (RAG + Event-Driven)
- **Semana 7:** Módulos 6-7 (Frameworks alternativos + Herramientas)
- **Semanas 8-10:** Módulo 8 (Proyecto Final)

### Práctica Recomendada
1. Cada concepto debe implementarse en código
2. Crear repositorio personal con ejemplos
3. Participar en comunidades y code reviews
4. Construir portfolio de agentes
5. Contribuir a proyectos open-source

---

## ✅ Checklist Pre-Curso

Antes de comenzar los laboratorios, asegúrate de tener:

### Cuentas y APIs (Gratuitas/Trial)
- [ ] Cuenta OpenAI + API key
- [ ] Cuenta Anthropic Claude + API key
- [ ] GitHub account
- [ ] LangSmith account (free tier)
- [ ] Pinecone account (free tier) o Chroma local
- [ ] Docker Desktop instalado

### Herramientas de Desarrollo
- [ ] Python 3.10+ instalado
- [ ] VS Code o PyCharm
- [ ] Git configurado
- [ ] Postman/Insomnia para testing APIs
- [ ] Terminal/CLI familiaridad

### Conocimientos Previos
- [ ] Python intermedio (async, decorators, typing)
- [ ] FastAPI o Flask básico
- [ ] Docker básico (build, run, compose)
- [ ] Git y GitHub workflow
- [ ] REST APIs y JSON

### Setup Inicial (Day 0)
```bash
# Crear directorio del curso
mkdir ai-agents-course && cd ai-agents-course

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar paquetes base
pip install langchain langgraph langchain-openai langchain-anthropic
pip install jupyter ipykernel python-dotenv
pip install fastapi uvicorn

# Configurar .env
echo "OPENAI_API_KEY=your-key" > .env
echo "ANTHROPIC_API_KEY=your-key" >> .env

# Verificar instalación
python -c "import langchain; print(langchain.__version__)"
```

### Repositorio del Curso
```bash
# Clonar template de inicio (ejemplo)
git clone https://github.com/langchain-ai/langchain
cd langchain/cookbook

# Crear tu propio repo para labs
gh repo create ai-agents-labs --public
```

---

## 🎯 Ruta de Aprendizaje Sugerida

### Opción 1: Full-Time (4 semanas intensivas)
- **Semana 1:** Módulos 1-3 (Fundamentos + LangChain + LangGraph)
- **Semana 2:** Módulos 4-5 (RAG + Event-Driven)
- **Semana 3:** Módulos 6-7 (Frameworks + Herramientas)
- **Semana 4:** Módulo 8 (Proyecto Final)

### Opción 2: Part-Time (8-10 semanas)
- **2 semanas por cada 2 módulos**
- 10-15 horas semanales
- 1-2 labs por sesión

### Opción 3: Weekend Warrior (12 semanas)
- **Sábados:** Teoría + 1 lab
- **Domingos:** 1-2 labs adicionales
- Review semanal

---

## 🏆 Certificación y Portfolio

Al completar el curso, tendrás:

1. **35+ Labs** en tu GitHub
2. **5 Proyectos** de complejidad creciente
3. **1 Proyecto Final** production-ready
4. **Portfolio público** demostrable
5. **Blog posts** documentando learnings (opcional)

### Template de Portfolio
```markdown
# AI Agents Portfolio - [Tu Nombre]

## 🤖 Proyectos Destacados
1. [Customer Support Agent] - RAG + Multi-tool
2. [Research Assistant] - Multi-source RAG + Citations
3. [Code Assistant] - Safe execution + GitHub integration

## 🛠️ Tech Stack
- Frameworks: LangChain, LangGraph, CrewAI
- Models: GPT-4, Claude 3.5 Sonnet
- Vector DBs: Pinecone, Qdrant
- Infra: Docker, Kubernetes, AWS

## 📊 Métricas
- 35+ labs completados
- 100+ hours de código
- 15+ repositorios públicos
```

---

## ⚡ Quick Start

```python
# Instalación base
pip install langchain langgraph langchain-openai langchain-anthropic
pip install chromadb pinecone-client
pip install langsmith phoenix

# Ejemplo básico
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# Tu primer agente...
```

**¡Comienza tu viaje en el desarrollo de agentes de IA! 🚀**