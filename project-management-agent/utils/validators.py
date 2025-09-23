from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class ProjectValidator:
    """Validador para datos de proyecto"""
    
    @staticmethod
    def validate_project_name(name: str) -> bool:
        """Validar nombre de proyecto"""
        if not name or len(name.strip()) < 3:
            return False
        
        pattern = r'^[a-zA-Z0-9\s\-_\.]+$'
        return bool(re.match(pattern, name.strip()))
    
    @staticmethod
    def validate_methodology(methodology: str) -> bool:
        """Validar metodología"""
        valid_methodologies = ['PMI', 'SAFe', 'Hybrid', 'Agile', 'Waterfall']
        return methodology in valid_methodologies
    
    @staticmethod
    def validate_project_data(project_data: Dict) -> Dict[str, List[str]]:
        """Validar datos completos de proyecto"""
        errors = {}
        
        required_fields = ['name', 'methodology', 'type', 'description']
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                if 'required' not in errors:
                    errors['required'] = []
                errors['required'].append(f"Campo requerido: {field}")
        
        return errors
