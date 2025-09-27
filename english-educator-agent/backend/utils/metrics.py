"""
Prometheus metrics for monitoring.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import functools
import time
import logging

logger = logging.getLogger(__name__)

# Define metrics
user_sessions = Counter(
    'user_sessions_total',
    'Total number of user sessions',
    ['user_id', 'session_type']
)

agent_response_time = Histogram(
    'agent_response_seconds',
    'Agent response time in seconds',
    ['agent_name'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

llm_tokens_used = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'agent', 'type']  # type: prompt or completion
)

exercise_accuracy = Histogram(
    'exercise_accuracy_percent',
    'Exercise completion accuracy percentage',
    ['level', 'exercise_type'],
    buckets=(0, 20, 40, 60, 80, 100)
)

api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_latency = Histogram(
    'api_latency_seconds',
    'API request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
)

db_query_time = Histogram(
    'db_query_seconds',
    'Database query execution time',
    ['query_type'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0)
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Application info
app_info = Info('app_info', 'Application information')


def track_agent_time(agent_name: str):
    """Decorator to track agent response time."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                agent_response_time.labels(agent_name=agent_name).observe(duration)
                logger.debug(f"{agent_name} took {duration:.2f}s")
        return wrapper
    return decorator


def track_llm_tokens(model: str, agent: str):
    """Decorator to track LLM token usage."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Extract token usage if available
            if hasattr(result, 'usage'):
                usage = result.usage
                llm_tokens_used.labels(
                    model=model,
                    agent=agent,
                    type='prompt'
                ).inc(usage.prompt_tokens)
                llm_tokens_used.labels(
                    model=model,
                    agent=agent,
                    type='completion'
                ).inc(usage.completion_tokens)
            
            return result
        return wrapper
    return decorator


def track_api_request(method: str, endpoint: str):
    """Decorator to track API requests."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                api_requests.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                api_latency.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator


def register_metrics():
    """Register application info metrics."""
    from config import settings
    
    app_info.info({
        'app_name': settings.APP_NAME,
        'environment': settings.ENVIRONMENT,
        'version': '1.0.0'
    })
    
    logger.info("Prometheus metrics registered")
