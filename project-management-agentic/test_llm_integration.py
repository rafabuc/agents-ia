#!/usr/bin/env python3
"""
Test script to validate LLM integration with BaseAgent
Tests that agents correctly use self.llm instead of ClaudeClient
"""

import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.project_manager_agent import ProjectManagerAgent
from agents.document_agent import DocumentAgent
from agents.risk_management_agent import RiskManagementAgent


def test_project_manager_agent_llm():
    """Test ProjectManagerAgent uses BaseAgent's LLM"""
    print("🧪 Testing ProjectManagerAgent LLM integration...")

    try:
        # Mock LLM response
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_response = Mock()
            mock_response.content = '{"intent": "general_query", "confidence": 0.8, "parameters": {}}'
            mock_claude_instance = Mock()
            mock_claude_instance.invoke.return_value = mock_response
            mock_claude.return_value = mock_claude_instance

            # Create agent
            agent = ProjectManagerAgent()

            # Verify LLM is initialized
            assert hasattr(agent, 'llm'), "Agent should have llm attribute"

            # Test intent analysis (should not fail)
            result = agent._analyze_intent_with_llm("test query")
            assert isinstance(result, dict), "Should return dict"

            print("✅ ProjectManagerAgent LLM integration working")
            return True

    except Exception as e:
        print(f"❌ ProjectManagerAgent test failed: {str(e)}")
        return False


def test_document_agent_llm():
    """Test DocumentAgent uses BaseAgent's LLM"""
    print("🧪 Testing DocumentAgent LLM integration...")

    try:
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_response = Mock()
            mock_response.content = '{"intent": "general_document", "confidence": 0.8, "parameters": {}}'
            mock_claude_instance = Mock()
            mock_claude_instance.invoke.return_value = mock_response
            mock_claude.return_value = mock_claude_instance

            agent = DocumentAgent()

            assert hasattr(agent, 'llm'), "Agent should have llm attribute"

            result = agent._analyze_document_intent("test document query")
            assert isinstance(result, dict), "Should return dict"

            print("✅ DocumentAgent LLM integration working")
            return True

    except Exception as e:
        print(f"❌ DocumentAgent test failed: {str(e)}")
        return False


def test_risk_management_agent_llm():
    """Test RiskManagementAgent uses BaseAgent's LLM"""
    print("🧪 Testing RiskManagementAgent LLM integration...")

    try:
        with patch('langchain_anthropic.ChatAnthropic') as mock_claude:
            mock_response = Mock()
            mock_response.content = '{"intent": "general_risk", "confidence": 0.8, "parameters": {}}'
            mock_claude_instance = Mock()
            mock_claude_instance.invoke.return_value = mock_response
            mock_claude.return_value = mock_claude_instance

            agent = RiskManagementAgent()

            assert hasattr(agent, 'llm'), "Agent should have llm attribute"

            result = agent._analyze_risk_intent("test risk query")
            assert isinstance(result, dict), "Should return dict"

            print("✅ RiskManagementAgent LLM integration working")
            return True

    except Exception as e:
        print(f"❌ RiskManagementAgent test failed: {str(e)}")
        return False


def test_no_claude_client_imports():
    """Verify that agents don't import ClaudeClient anymore"""
    print("🧪 Testing that ClaudeClient imports are removed...")

    try:
        # Read agent files and check for ClaudeClient imports
        agent_files = [
            'agents/project_manager_agent.py',
            'agents/document_agent.py',
            'agents/risk_management_agent.py'
        ]

        for file_path in agent_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for ClaudeClient imports (should not exist)
            if 'from core.claude_client import ClaudeClient' in content:
                print(f"❌ Found ClaudeClient import in {file_path}")
                return False

            if 'self.claude_client = ClaudeClient()' in content:
                print(f"❌ Found ClaudeClient initialization in {file_path}")
                return False

            # Check for proper LLM usage
            if 'self.llm.invoke(' not in content:
                print(f"❌ No LLM usage found in {file_path}")
                return False

        print("✅ No ClaudeClient imports found, proper LLM usage detected")
        return True

    except Exception as e:
        print(f"❌ Import check failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting LLM Integration Tests...\n")

    tests = [
        test_project_manager_agent_llm,
        test_document_agent_llm,
        test_risk_management_agent_llm,
        test_no_claude_client_imports
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line for readability

    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! LLM integration is working correctly.")
        print("\n💡 Benefits achieved:")
        print("  • ✅ Consistent LLM configuration across all agents")
        print("  • ✅ Centralized LLM management in BaseAgent")
        print("  • ✅ No duplicate ClaudeClient instances")
        print("  • ✅ Easier maintenance and configuration")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)