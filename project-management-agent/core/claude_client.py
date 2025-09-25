# core/claude_client.py
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ChatResponse:
    """Respuesta de chat estructurada"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str

class ClaudeClient:
    """Cliente para interactuar con la API de Claude"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):#claude-3-5-sonnet-20241022
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print(f"✅ Claude client initialized with model: {self.model}")
            except ImportError:
                print("⚠️ anthropic package not installed. Run: pip install anthropic")
                self.client = None
        else:
            print("⚠️ ANTHROPIC_API_KEY not found. Using fallback mode.")
    
    def chat(self, message: str, system_prompt: str = None, 
             conversation_history: List[Dict] = None, max_tokens: int = 1500) -> ChatResponse:
        """Enviar mensaje a Claude y obtener respuesta"""
        
        if not self.client:
            return ChatResponse(
                content="⚠️ Cliente Claude no disponible. Configura ANTHROPIC_API_KEY.",
                tokens_used=0,
                model=self.model,
                finish_reason="no_client"
            )
        
        try:
            # Construir mensajes para la API
            messages = []
            
            # Agregar historial de conversación si existe
            if conversation_history:
                for msg in conversation_history[-6:]:  # Últimos 6 mensajes para contexto
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content'][:1000]  # Limitar longitud para contexto
                    })
            
            # Agregar mensaje actual
            messages.append({
                "role": "user",
                "content": message
            })
            
            # System prompt por defecto si no se proporciona
            if not system_prompt:
                system_prompt = """Eres PM-Agent, un asistente experto en Project Management. 
                Tu especialidad incluye metodologías como Scrum, Kanban, PMI, SAFe, y herramientas de gestión de proyectos.
                
                Proporciona respuestas prácticas, estructuradas y accionables. 
                Usa ejemplos concretos cuando sea posible.
                Mantén un tono profesional pero accesible."""
            
            # Llamar a la API de Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )
            
            # Extraer información de la respuesta
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return ChatResponse(
                content=content,
                tokens_used=tokens_used,
                model=self.model,
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            return ChatResponse(
                content=f"❌ Error de Claude API: {str(e)}",
                tokens_used=0,
                model=self.model,
                finish_reason="error"
            )
    
    def generate_summary(self, content: str, max_tokens: int = 300) -> str:
        """Generar resumen de contenido"""
        if not self.client:
            return "Resumen no disponible. Cliente Claude no configurado."
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.5,
                system="Eres un experto en crear resúmenes concisos y útiles de conversaciones de project management.",
                messages=[{
                    "role": "user",
                    "content": f"Crea un resumen conciso de esta conversación, destacando los temas principales, decisiones tomadas y próximos pasos:\n\n{content[:4000]}"
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generando resumen: {str(e)}"