import os
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger

class TemplateEngine:
    """Motor de plantillas para documentos de proyecto"""
    
    def __init__(self):
        self.templates_path = Path("./templates")
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self.env.globals.update({
            'now': datetime.now,
            'format_date': self._format_date,
        })
        
        logger.info("Template engine initialized")
    
    def _format_date(self, date_obj, format_str: str = "%Y-%m-%d") -> str:
        """Formatear fecha"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except ValueError:
                return date_obj
        return date_obj.strftime(format_str)
    
    def generate_document(self, document_type: str, context: dict) -> str:
        """Generar documento usando plantilla"""
        try:
            methodology = context.get('methodology', 'PMI')
            template_name = f"{methodology.lower()}_templates/{document_type}.md"
            
            try:
                template = self.env.get_template(template_name)
            except Exception:
                template = self.env.get_template(f"common_templates/{document_type}.md")
            
            content = template.render(**context)
            logger.info(f"Document generated: {document_type}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating document {document_type}: {e}")
            return self._generate_fallback_document(document_type, context)
    
    def _generate_fallback_document(self, document_type: str, context: dict) -> str:
        """Generar documento básico si no hay plantilla"""
        project = context.get('project', {})
        
        return f"""# {document_type.replace('_', ' ').title()}
**Proyecto:** {project.get('name', 'TBD')}
**Fecha:** {datetime.now().strftime('%Y-%m-%d')}
**Metodología:** {project.get('methodology', 'TBD')}

## Descripción
Este documento será completado según los requerimientos específicos del proyecto.

## Secciones Principales
- Objetivos
- Alcance
- Entregables
- Cronograma
- Recursos
- Riesgos

---
*Documento generado automáticamente.*
"""
