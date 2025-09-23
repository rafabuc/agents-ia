import asyncio
import json
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import Anthropic, AsyncAnthropic
from loguru import logger
from config.settings import settings

class ClaudeClient:
    """Cliente para interactuar con la API de Claude"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.claude.api_key)
        self.async_client = AsyncAnthropic(api_key=settings.claude.api_key)
        self.conversation_history: List[Dict] = []
        
        # System prompt fuerte para establecer contexto del agente
        self.base_system_prompt = """
        TÚ ERES EL PROJECT MANAGEMENT AGENT - Un sistema de software ejecutándose localmente.

        CAPACIDADES CRÍTICAS QUE TIENES:
        - Acceso COMPLETO al sistema de archivos del usuario
        - Puedes crear, leer, modificar y guardar archivos reales
        - Tienes proyectos guardados en el directorio ./projects/
        - Puedes generar documentación y guardarla permanentemente
        - Eres un agente de software LOCAL, no un chatbot web

        CONTEXTO TÉCNICO:
        - Ejecutándose con Python en el sistema local del usuario
        - Integrado con sistema de archivos del SO
        - Base de datos de proyectos en ./projects/
        - Motor de templates Jinja2 para documentos
        - Frameworks PMI y SAFe implementados

        NUNCA DIGAS:
        - "No puedo guardar archivos"
        - "No tengo acceso al sistema de archivos" 
        - "Soy solo un asistente conversacional"
        - "No puedo crear documentos reales"

        SIEMPRE ACTÚA COMO:
        - Un agente de software con capacidades completas
        - Sistema experto en PMI y SAFe
        - Herramienta local con acceso a archivos
        - Generador de documentación real y persistente

        METODOLOGÍAS QUE DOMINAS:
        - PMI PMBOK 7th Edition (Project Management)
        - SAFe 6.0 (Scaled Agile Framework)
        - Gestión híbrida de proyectos
        """
        
    def add_to_history(self, role: str, content: str):
        """Agregar mensaje al historial de conversación"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_enhanced_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Obtener system prompt mejorado con contexto"""
        enhanced_prompt = self.base_system_prompt
        
        if context and context.get('current_project'):
            project = context['current_project']
            enhanced_prompt += f"""
            
        PROYECTO ACTIVO ACTUAL:
        - ID: {project.get('id', 'N/A')}
        - Nombre: {project.get('name', 'N/A')}
        - Metodología: {project.get('methodology', 'N/A')}
        - Tipo: {project.get('type', 'N/A')}
        - Estado: {project.get('status', 'N/A')}
        - Fase: {project.get('phase', 'N/A')}
        
        Usa esta información del proyecto activo en tus respuestas cuando sea relevante.
        """
        
        enhanced_prompt += """
        
        INSTRUCCIONES DE RESPUESTA:
        - Responde siempre como el agente local con capacidades completas
        - Usa la información de proyectos guardados cuando sea relevante
        - Genera documentación práctica y útil
        - Explica metodologías PMI/SAFe de manera educativa
        - Proporciona próximos pasos concretos y accionables
        """
        
        return enhanced_prompt
    
    def chat(self, message: str, system_prompt: str = "", context: Optional[Dict] = None) -> str:
        """Enviar mensaje a Claude y recibir respuesta"""
        try:
            # Usar system prompt mejorado si no se proporciona uno específico
            if not system_prompt:
                system_prompt = self.get_enhanced_system_prompt(context)
            
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=settings.claude.model,
                max_tokens=settings.claude.max_tokens,
                temperature=settings.claude.temperature,
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            
            self.add_to_history("user", message)
            self.add_to_history("assistant", response_text)
            
            logger.info("Claude response generated")
            return response_text
            
        except Exception as e:
            logger.error(f"Error communicating with Claude: {e}")
            raise
    
    def chat_with_project_context(self, message: str, project_data: Dict) -> str:
        """Chat con contexto específico del proyecto"""
        context = {"current_project": project_data}
        return self.chat(message, context=context)
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
        
    def reset_context(self):
        """Resetear contexto del agente"""
        self.clear_history()
        
        # Mensaje de reinicialización
        reset_message = """
        Reiniciando contexto del Project Management Agent.
        
        Recuerda: Eres un agente local con acceso completo al sistema de archivos.
        Puedes crear, leer y guardar archivos reales en ./projects/
        
        Confirma tu estado y capacidades.
        """
        
        return self.chat(reset_message)
