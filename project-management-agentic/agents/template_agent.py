from typing import Dict, Any, List
import json
import os
from datetime import datetime
from jinja2 import Template, FileSystemLoader, Environment

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .base_agent import BaseAgent
from storage.file_manager import FileManager
from config.settings import settings
from utils.logger import logger


class TemplateAgent(BaseAgent):
    """Agent specialized in filling and managing project templates."""
    
    def __init__(self):
        super().__init__(
            name="Template_Agent",
            description="Fills project templates with data and generates formatted documents"
        )
        self.file_manager = FileManager()
        try:
            self.template_env = Environment(
                loader=FileSystemLoader(settings.templates_path),
                trim_blocks=True,
                lstrip_blocks=True
            )
        except Exception as e:
            logger.warning(f"Template environment not available: {str(e)}")
            self.template_env = None
    
    def get_system_prompt(self) -> str:
        return """You are an expert in project document template management and generation.
        
        Your responsibilities include:
        1. Filling project templates with provided data
        2. Generating formatted documents from templates
        3. Managing template libraries and versions
        4. Creating custom templates based on requirements
        5. Ensuring document consistency and quality
        6. Converting between different document formats
        7. Validating template data completeness
        8. Managing template inheritance and includes
        
        You work with Jinja2 templates and can generate various output formats.
        Always ensure data integrity and template syntax correctness.
        Provide helpful feedback on missing or invalid template data.
        """
    
    def _create_agent(self) -> AgentExecutor:
        """Create the template agent."""
        tools = [
            self._fill_template_tool(),
            self._list_templates_tool(),
            self._validate_template_data_tool(),
            self._create_custom_template_tool(),
            self._generate_document_tool()
        ]
        
        # Mock implementation for demo
        class MockAgentExecutor:
            def __init__(self, tools):
                self.tools = tools
            
            async def ainvoke(self, inputs):
                return {"output": f"Template Agent processed: {inputs.get('input', '')}"}
        
        return MockAgentExecutor(tools)
    
    def _fill_template_tool(self) -> Tool:
        """Tool to fill templates with data."""
        def fill_template(template_data: str) -> str:
            try:
                data = json.loads(template_data)
                template_name = data.get("template_name")
                project_id = data.get("project_id")
                template_data = data.get("data", {})
                output_filename = data.get("output_filename")
                
                if not template_name:
                    return "Error: template_name is required"
                
                # Load and render template
                try:
                    if self.template_env:
                        template = self.template_env.get_template(template_name)
                        rendered_content = template.render(**template_data)
                    else:
                        # Fallback to simple template
                        rendered_content = self._render_simple_template(template_name, template_data)
                        
                except Exception as e:
                    return f"Error loading template '{template_name}': {str(e)}"
                
                # Save rendered document
                if project_id:
                    file_path = self.file_manager.save_project_document(
                        project_id=project_id,
                        document_type="filled_template",
                        content=rendered_content,
                        filename=output_filename or f"filled_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    
                    # Store in database
                    self.db_manager.create_project_document(
                        project_id=project_id,
                        document_type="filled_template",
                        file_path=file_path,
                        content=rendered_content
                    )
                    
                    return f"Template filled successfully and saved to: {file_path}"
                else:
                    return f"Template filled successfully:\n\n{rendered_content}"
                
            except Exception as e:
                logger.error(f"Error filling template: {str(e)}")
                return f"Error filling template: {str(e)}"
        
        return Tool(
            name="fill_template",
            description="Fill a template with provided data. Input should be JSON with template_name, optional project_id, data object, and optional output_filename.",
            func=fill_template
        )
    
    def _list_templates_tool(self) -> Tool:
        """Tool to list available templates."""
        def list_templates(category: str = "") -> str:
            try:
                templates = []
                template_dir = settings.templates_path
                
                if os.path.exists(template_dir):
                    for filename in os.listdir(template_dir):
                        if filename.endswith(('.jinja2', '.j2')):
                            template_info = {
                                "name": filename,
                                "path": os.path.join(template_dir, filename),
                                "size": os.path.getsize(os.path.join(template_dir, filename)),
                                "modified": datetime.fromtimestamp(
                                    os.path.getmtime(os.path.join(template_dir, filename))
                                ).strftime("%Y-%m-%d %H:%M:%S")
                            }
                            templates.append(template_info)
                
                # Add built-in templates
                built_in_templates = [
                    {"name": "project_charter", "description": "Standard project charter template"},
                    {"name": "cost_estimate", "description": "Cost estimation template"},
                    {"name": "risk_register", "description": "Risk management template"}
                ]
                
                result = "Available templates:\n\n"
                
                # Built-in templates
                result += "**Built-in Templates:**\n"
                for template in built_in_templates:
                    result += f"- **{template['name']}**: {template['description']}\n"
                
                # File-based templates
                if templates:
                    result += "\n**File Templates:**\n"
                    for template in templates:
                        result += f"- **{template['name']}**\n"
                        result += f"  - Path: {template['path']}\n"
                        result += f"  - Size: {template['size']} bytes\n"
                        result += f"  - Modified: {template['modified']}\n\n"
                
                return result
                
            except Exception as e:
                return f"Error listing templates: {str(e)}"
        
        return Tool(
            name="list_templates",
            description="List all available templates in the templates directory.",
            func=list_templates
        )
    
    def _validate_template_data_tool(self) -> Tool:
        """Tool to validate template data against template requirements."""
        def validate_data(validation_data: str) -> str:
            try:
                data = json.loads(validation_data)
                template_name = data.get("template_name")
                template_data = data.get("data", {})
                
                if not template_name:
                    return "Error: template_name is required"
                
                # Basic validation for built-in templates
                required_fields = {
                    "project_charter": ["project_name", "description"],
                    "cost_estimate": ["project_id", "base_cost"],
                    "risk_register": ["project_id", "risks"]
                }
                
                if template_name in required_fields:
                    missing_fields = []
                    for field in required_fields[template_name]:
                        if field not in template_data or not template_data[field]:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return f"Template data validation failed. Missing required fields: {', '.join(missing_fields)}"
                
                return f"Template data validation successful for '{template_name}'"
                
            except Exception as e:
                return f"Error validating template data: {str(e)}"
        
        return Tool(
            name="validate_template_data",
            description="Validate that provided data is compatible with template requirements. Input should be JSON with template_name and data object.",
            func=validate_data
        )
    
    def _create_custom_template_tool(self) -> Tool:
        """Tool to create custom templates."""
        def create_template(template_info: str) -> str:
            try:
                data = json.loads(template_info)
                template_name = data.get("template_name")
                template_content = data.get("content")
                description = data.get("description", "")
                
                if not template_name or not template_content:
                    return "Error: template_name and content are required"
                
                # Ensure .jinja2 extension
                if not template_name.endswith(('.jinja2', '.j2')):
                    template_name += '.jinja2'
                
                # Create template file
                template_path = os.path.join(settings.templates_path, template_name)
                
                # Add template header with metadata
                full_content = f"""{{# Template: {template_name} #}}
{{# Description: {description} #}}
{{# Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} #}}

{template_content}
"""
                
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
                return f"Custom template '{template_name}' created successfully at: {template_path}"
                
            except Exception as e:
                return f"Error creating custom template: {str(e)}"
        
        return Tool(
            name="create_custom_template",
            description="Create a custom Jinja2 template. Input should be JSON with template_name, content, and optional description.",
            func=create_template
        )
    
    def _generate_document_tool(self) -> Tool:
        """Tool to generate documents in different formats."""
        def generate_document(doc_data: str) -> str:
            try:
                data = json.loads(doc_data)
                project_id = data.get("project_id")
                template_name = data.get("template_name")
                template_data = data.get("data", {})
                output_format = data.get("format", "markdown")  # markdown, html, txt
                output_filename = data.get("output_filename")
                
                if not template_name:
                    return "Error: template_name is required"
                
                # Fill template
                if self.template_env:
                    try:
                        template = self.template_env.get_template(template_name)
                        rendered_content = template.render(**template_data)
                    except:
                        rendered_content = self._render_simple_template(template_name, template_data)
                else:
                    rendered_content = self._render_simple_template(template_name, template_data)
                
                # Generate filename if not provided
                if not output_filename:
                    base_name = template_name.replace('.jinja2', '').replace('.j2', '')
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_filename = f"{base_name}_{timestamp}.{output_format}"
                
                # Save document
                if project_id:
                    file_path = self.file_manager.save_project_document(
                        project_id=project_id,
                        document_type=f"generated_{output_format}",
                        content=rendered_content,
                        filename=output_filename
                    )
                    
                    return f"Document generated successfully: {file_path}"
                else:
                    return f"Document generated successfully:\n\n{rendered_content}"
                
            except Exception as e:
                return f"Error generating document: {str(e)}"
        
        return Tool(
            name="generate_document",
            description="Generate a document from template in specified format (markdown, html, txt). Input should be JSON with template_name, data, format, optional project_id and output_filename.",
            func=generate_document
        )
    
    def _render_simple_template(self, template_name: str, data: Dict) -> str:
        """Simple template rendering fallback."""
        
        if template_name == "project_charter":
            return f"""# PROJECT CHARTER

## PROJECT INFORMATION
- **Project Name:** {data.get('project_name', 'TBD')}
- **Project Manager:** {data.get('project_manager', 'TBD')}
- **Start Date:** {data.get('start_date', 'TBD')}
- **Budget:** {data.get('budget', 'TBD')}

## PROJECT DESCRIPTION
{data.get('description', 'Project description to be defined')}

## PROJECT OBJECTIVES
{data.get('objectives', 'Objectives to be defined')}

## PROJECT SCOPE
### In Scope:
{data.get('scope_inclusions', 'Scope to be defined')}

## STAKEHOLDERS
{data.get('stakeholders', 'Stakeholders to be identified')}

---
*Document Version:* 1.0
*Created On:* {datetime.now().strftime('%Y-%m-%d')}
"""
        
        elif template_name == "cost_estimate":
            return f"""# COST ESTIMATE

**Project ID:** {data.get('project_id', 'TBD')}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## COST SUMMARY
- **Base Cost:** ${data.get('base_cost', 0):,.2f}
- **Contingency (10%):** ${data.get('base_cost', 0) * 0.1:,.2f}
- **Total Estimate:** ${data.get('base_cost', 0) * 1.1:,.2f}

## ASSUMPTIONS
- Standard labor rates applied
- Current material costs
- No major scope changes

## APPROVAL
Prepared by: {data.get('estimator', 'Cost Analyst')}
Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        else:
            return f"# {template_name.upper()}\\n\\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n{json.dumps(data, indent=2)}"