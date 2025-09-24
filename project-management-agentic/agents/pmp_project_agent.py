from typing import Dict, Any, List
import json
import os
from datetime import datetime

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .base_agent import BaseAgent
from storage.file_manager import FileManager
from models.project import Project, ProjectStatus
from config.settings import settings
from utils.logger import logger


class PMPProjectAgent(BaseAgent):
    """Agent specialized in PMP project creation and management."""
    
    def __init__(self):
        super().__init__(
            name="PMP_Project_Agent",
            description="Creates and manages projects using PMP and SAFe methodologies"
        )
        self.file_manager = FileManager()
    
    def get_system_prompt(self) -> str:
        return """You are an expert Project Management Professional (PMP) and SAFe specialist. 
        You help create comprehensive project documentation following PMI standards and SAFe practices.
        
        Your responsibilities include:
        1. Creating project charters
        2. Developing Work Breakdown Structures (WBS)
        3. Defining project scope and deliverables
        4. Creating project schedules and milestones
        5. Identifying stakeholders and their roles
        6. Developing risk registers
        7. Creating communication plans
        8. Following PMP best practices and SAFe principles
        
        Always provide structured, detailed responses that can be used as official project documentation.
        Save all generated documents to the file system for future reference.
        """
    
    def _create_agent(self) -> AgentExecutor:
        """Create the PMP project agent."""
        tools = [
            self._create_project_tool(),
            self._save_project_document_tool(),
            self._get_project_template_tool(),
            self._update_project_status_tool()
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_project_tool(self) -> Tool:
        """Tool to create a new project in the database."""
        def create_project(project_data: str) -> str:
            try:
                data = json.loads(project_data)
                
                # Create project in database
                project = self.db_manager.create_project(
                    name=data.get("name"),
                    description=data.get("description"),
                    methodology=data.get("methodology", "PMP"),
                    project_data=data
                )
                
                # Create project directory
                project_dir = self.file_manager.create_project_directory(project.id)
                
                logger.info(f"Created project {project.name} with ID {project.id}")
                
                return f"Project '{project.name}' created successfully with ID {project.id}. Project directory: {project_dir}"
                
            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                return f"Error creating project: {str(e)}"
        
        return Tool(
            name="create_project",
            description="Create a new project with the given data. Input should be JSON string with project information.",
            func=create_project
        )
    
    def _save_project_document_tool(self) -> Tool:
        """Tool to save project documents."""
        def save_document(document_info: str) -> str:
            try:
                data = json.loads(document_info)
                project_id = data.get("project_id")
                document_type = data.get("document_type")
                content = data.get("content")
                filename = data.get("filename")
                
                if not all([project_id, document_type, content]):
                    return "Error: Missing required fields (project_id, document_type, content)"
                
                # Save to file system
                file_path = self.file_manager.save_project_document(
                    project_id=project_id,
                    document_type=document_type,
                    content=content,
                    filename=filename
                )
                
                # Save to database
                self.db_manager.create_project_document(
                    project_id=project_id,
                    document_type=document_type,
                    file_path=file_path,
                    content=content
                )
                
                return f"Document saved successfully: {file_path}"
                
            except Exception as e:
                logger.error(f"Error saving document: {str(e)}")
                return f"Error saving document: {str(e)}"
        
        return Tool(
            name="save_project_document",
            description="Save a project document to file system and database. Input should be JSON with project_id, document_type, content, and optional filename.",
            func=save_document
        )
    
    def _get_project_template_tool(self) -> Tool:
        """Tool to get project templates."""
        def get_template(template_type: str) -> str:
            try:
                templates = {
                    "project_charter": self._get_project_charter_template(),
                    "wbs": self._get_wbs_template(),
                    "risk_register": self._get_risk_register_template(),
                    "stakeholder_register": self._get_stakeholder_register_template(),
                    "communication_plan": self._get_communication_plan_template()
                }
                
                template = templates.get(template_type.lower())
                if template:
                    return template
                else:
                    available = ", ".join(templates.keys())
                    return f"Template not found. Available templates: {available}"
                    
            except Exception as e:
                return f"Error getting template: {str(e)}"
        
        return Tool(
            name="get_project_template",
            description="Get a project template by type. Available types: project_charter, wbs, risk_register, stakeholder_register, communication_plan",
            func=get_template
        )
    
    def _update_project_status_tool(self) -> Tool:
        """Tool to update project status."""
        def update_status(status_data: str) -> str:
            try:
                data = json.loads(status_data)
                project_id = data.get("project_id")
                new_status = data.get("status")
                
                if not project_id or not new_status:
                    return "Error: Missing project_id or status"
                
                # Update in database
                success = self.db_manager.update_project_status(project_id, new_status)
                
                if success:
                    return f"Project {project_id} status updated to {new_status}"
                else:
                    return f"Error updating project status"
                    
            except Exception as e:
                return f"Error updating project status: {str(e)}"
        
        return Tool(
            name="update_project_status",
            description="Update project status. Input should be JSON with project_id and status.",
            func=update_status
        )
    
    def _get_project_charter_template(self) -> str:
        return """
# PROJECT CHARTER TEMPLATE

## 1. PROJECT INFORMATION
- Project Name: 
- Project Manager: 
- Sponsor: 
- Start Date: 
- Expected End Date: 
- Budget: 

## 2. PROJECT DESCRIPTION
[Detailed description of the project]

## 3. PROJECT OBJECTIVES
- Primary Objective:
- Secondary Objectives:
- Success Criteria:

## 4. PROJECT SCOPE
### In Scope:
- [List items included in project scope]

### Out of Scope:
- [List items explicitly excluded]

## 5. HIGH-LEVEL REQUIREMENTS
- [List major requirements]

## 6. HIGH-LEVEL RISKS
- [Identify major risks]

## 7. HIGH-LEVEL ASSUMPTIONS
- [List key assumptions]

## 8. HIGH-LEVEL CONSTRAINTS
- [List major constraints]

## 9. STAKEHOLDERS
| Name | Role | Contact | Influence/Interest |
|------|------|---------|-------------------|
|      |      |         |                   |

## 10. AUTHORIZATION
Project Manager Signature: _______________ Date: ___________
Sponsor Signature: _______________ Date: ___________
"""
    
    def _get_wbs_template(self) -> str:
        return """
# WORK BREAKDOWN STRUCTURE (WBS)

## 1.0 [PROJECT NAME]
### 1.1 Project Management
    1.1.1 Project Planning
    1.1.2 Project Monitoring & Control
    1.1.3 Project Closure

### 1.2 [MAJOR DELIVERABLE 1]
    1.2.1 [Sub-deliverable 1.1]
    1.2.2 [Sub-deliverable 1.2]
    1.2.3 [Sub-deliverable 1.3]

### 1.3 [MAJOR DELIVERABLE 2]
    1.3.1 [Sub-deliverable 2.1]
    1.3.2 [Sub-deliverable 2.2]

### 1.4 Quality Assurance
    1.4.1 Quality Planning
    1.4.2 Quality Control
    1.4.3 Quality Improvement

### 1.5 Testing & Validation
    1.5.1 Test Planning
    1.5.2 Test Execution
    1.5.3 User Acceptance Testing
"""
    
    def _get_risk_register_template(self) -> str:
        return """
# RISK REGISTER

| ID | Risk Description | Category | Probability | Impact | Risk Score | Mitigation Strategy | Owner | Status |
|----|------------------|----------|-------------|---------|------------|-------------------|-------|---------|
| R001 | [Risk description] | Technical/Schedule/Budget/Resource | H/M/L | H/M/L | [P×I] | [Mitigation plan] | [Owner] | Open/Closed |
| R002 | | | | | | | | |

## Risk Categories:
- Technical: Technology, performance, quality issues
- Schedule: Timeline, dependency, resource availability
- Budget: Cost overruns, funding issues
- Resource: Staff availability, skill gaps
- External: Vendor, regulatory, market changes

## Probability/Impact Scale:
- High (H): > 70% / Major impact on project objectives
- Medium (M): 30-70% / Moderate impact on project objectives  
- Low (L): < 30% / Minor impact on project objectives
"""
    
    def _get_stakeholder_register_template(self) -> str:
        return """
# STAKEHOLDER REGISTER

| Name | Title/Role | Organization | Contact Info | Influence | Interest | Engagement Strategy |
|------|------------|--------------|--------------|-----------|----------|-------------------|
| [Name] | [Title] | [Org] | [Email/Phone] | H/M/L | H/M/L | [Strategy] |

## Influence/Interest Matrix:
- High Influence, High Interest: Manage Closely
- High Influence, Low Interest: Keep Satisfied  
- Low Influence, High Interest: Keep Informed
- Low Influence, Low Interest: Monitor

## Engagement Strategies:
- Regular meetings and updates
- Formal reporting
- Ad-hoc communications
- Consultation on key decisions
"""
    
    def _get_communication_plan_template(self) -> str:
        return """
# COMMUNICATION PLAN

## Communication Requirements

| Stakeholder | Information Needs | Frequency | Method | Responsible | Format |
|-------------|-------------------|-----------|---------|-------------|---------|
| Project Sponsor | Status updates, issues, decisions | Weekly | Email/Meeting | PM | Status Report |
| Project Team | Tasks, schedules, issues | Daily | Standup/Slack | PM | Verbal/Chat |
| End Users | Progress, training, go-live | Bi-weekly | Newsletter | PM | Email |

## Communication Methods:
- Face-to-face meetings
- Video conferences
- Email updates
- Project dashboard
- Status reports
- Team chat (Slack/Teams)

## Escalation Matrix:
| Issue Level | Escalate To | Timeline |
|-------------|-------------|----------|
| Level 1 - Team issues | Team Lead | Immediate |
| Level 2 - Project issues | Project Manager | 24 hours |
| Level 3 - Major issues | Project Sponsor | 48 hours |
"""