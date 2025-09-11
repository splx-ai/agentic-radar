"""
Tests for prompt hardening functionality.

These tests cover the prompt hardening pipeline, steps, and main functions.
"""

import os
from unittest.mock import Mock, patch, MagicMock

import pytest

from agentic_radar.graph import Agent
from agentic_radar.prompt_hardening.harden import harden_agent_prompts
from agentic_radar.prompt_hardening.pipeline import PromptHardeningPipeline, PromptHardeningStep
from agentic_radar.prompt_hardening.steps.openai_generator import OpenAIGeneratorStep
from agentic_radar.prompt_hardening.steps.pii_protection import PIIProtectionStep


class MockPromptHardeningStep(PromptHardeningStep):
    """Mock step for testing."""
    
    def __init__(self, transform_func=None):
        self.transform_func = transform_func or (lambda x: f"hardened: {x}")
    
    def harden(self, system_prompt: str) -> str:
        return self.transform_func(system_prompt)


class TestPromptHardeningPipeline:
    """Test the PromptHardeningPipeline class."""
    
    def test_pipeline_initialization(self):
        """Test pipeline can be initialized with steps."""
        step1 = MockPromptHardeningStep()
        step2 = MockPromptHardeningStep()
        pipeline = PromptHardeningPipeline([step1, step2])
        
        assert len(pipeline._steps) == 2
        assert pipeline._steps[0] is step1
        assert pipeline._steps[1] is step2
    
    def test_pipeline_empty_steps(self):
        """Test pipeline with no steps."""
        pipeline = PromptHardeningPipeline([])
        result = pipeline.run("test prompt")
        assert result == "test prompt"
    
    def test_pipeline_single_step(self):
        """Test pipeline with single step."""
        step = MockPromptHardeningStep(lambda x: x.upper())
        pipeline = PromptHardeningPipeline([step])
        
        result = pipeline.run("test prompt")
        assert result == "TEST PROMPT"
    
    def test_pipeline_multiple_steps(self):
        """Test pipeline applies steps in sequence."""
        step1 = MockPromptHardeningStep(lambda x: f"[{x}]")
        step2 = MockPromptHardeningStep(lambda x: x.upper())
        pipeline = PromptHardeningPipeline([step1, step2])
        
        result = pipeline.run("test")
        assert result == "[TEST]"
    
    def test_pipeline_step_chaining(self):
        """Test that steps are properly chained."""
        step1 = MockPromptHardeningStep(lambda x: x + " step1")
        step2 = MockPromptHardeningStep(lambda x: x + " step2")
        step3 = MockPromptHardeningStep(lambda x: x + " step3")
        pipeline = PromptHardeningPipeline([step1, step2, step3])
        
        result = pipeline.run("start")
        assert result == "start step1 step2 step3"


class TestHardenAgentPrompts:
    """Test the harden_agent_prompts function."""
    
    def test_harden_empty_agents_list(self):
        """Test hardening with empty agents list."""
        pipeline = PromptHardeningPipeline([])
        result = harden_agent_prompts([], pipeline)
        assert result == {}
    
    def test_harden_single_agent(self):
        """Test hardening single agent."""
        agent = Agent(name="test_agent", llm="gpt-4", system_prompt="original prompt")
        step = MockPromptHardeningStep(lambda x: f"hardened: {x}")
        pipeline = PromptHardeningPipeline([step])
        
        result = harden_agent_prompts([agent], pipeline)
        
        assert result == {"test_agent": "hardened: original prompt"}
    
    def test_harden_multiple_agents(self):
        """Test hardening multiple agents."""
        agent1 = Agent(name="agent1", llm="gpt-4", system_prompt="prompt1")
        agent2 = Agent(name="agent2", llm="gpt-3.5", system_prompt="prompt2")
        
        step = MockPromptHardeningStep(lambda x: f"hardened: {x}")
        pipeline = PromptHardeningPipeline([step])
        
        result = harden_agent_prompts([agent1, agent2], pipeline)
        
        expected = {
            "agent1": "hardened: prompt1",
            "agent2": "hardened: prompt2"
        }
        assert result == expected
    
    def test_harden_agents_with_exception(self):
        """Test hardening when pipeline raises exception."""
        agent = Agent(name="test_agent", llm="gpt-4", system_prompt="original prompt")
        
        def failing_step(x):
            raise ValueError("Step failed")
        
        step = MockPromptHardeningStep(failing_step)
        pipeline = PromptHardeningPipeline([step])
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            result = harden_agent_prompts([agent], pipeline)
        
        # Should fall back to original prompt
        assert result == {"test_agent": "original prompt"}
        mock_print.assert_called_once()


class TestOpenAIGeneratorStep:
    """Test the OpenAIGeneratorStep class."""
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('agentic_radar.prompt_hardening.steps.openai_generator.OpenAI')
    def test_openai_generator_initialization_openai(self, mock_openai):
        """Test OpenAIGeneratorStep initializes with OpenAI client."""
        step = OpenAIGeneratorStep()
        mock_openai.assert_called_once()
    
    @patch.dict(os.environ, {"AZURE_OPENAI_API_KEY": "test-key"})
    @patch('agentic_radar.prompt_hardening.steps.openai_generator.AzureOpenAI')
    def test_openai_generator_initialization_azure(self, mock_azure):
        """Test OpenAIGeneratorStep initializes with Azure client."""
        step = OpenAIGeneratorStep()
        mock_azure.assert_called_once()
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_generator_harden(self):
        """Test OpenAIGeneratorStep harden method."""
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices[0].message.content = "hardened prompt"
        mock_client.chat.completions.create.return_value = mock_completion
        
        step = OpenAIGeneratorStep()
        step.client = mock_client
        
        result = step.harden("original prompt")
        
        assert result == "hardened prompt"
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify the call parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o"
        assert len(call_args[1]["messages"]) == 2
        assert "Current Prompt:" in call_args[1]["messages"][1]["content"]
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_generator_exception_handling(self):
        """Test OpenAIGeneratorStep handles API exceptions."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        step = OpenAIGeneratorStep()
        step.client = mock_client
        
        with pytest.raises(Exception):
            step.harden("original prompt")


class TestPIIProtectionStep:
    """Test the PIIProtectionStep class."""
    
    def test_pii_protection_step_exists(self):
        """Test that PIIProtectionStep can be imported and instantiated."""
        # The step exists but may have minimal implementation
        step = PIIProtectionStep()
        assert isinstance(step, PromptHardeningStep)
    
    def test_pii_protection_step_harden_method(self):
        """Test that PIIProtectionStep has harden method."""
        step = PIIProtectionStep()
        
        # Test that the method exists and can be called
        result = step.harden("test prompt with potential PII: john@example.com")
        # The result should be a string (implementation may vary)
        assert isinstance(result, str)


class TestPromptHardeningIntegration:
    """Integration tests for the complete prompt hardening system."""
    
    def test_full_pipeline_integration(self):
        """Test complete pipeline with multiple steps."""
        agent = Agent(name="test_agent", llm="gpt-4", system_prompt="You are a helpful assistant.")
        
        # Create a pipeline with multiple steps
        step1 = MockPromptHardeningStep(lambda x: x.replace("helpful", "very helpful"))
        step2 = MockPromptHardeningStep(lambda x: x + " Please be concise.")
        pipeline = PromptHardeningPipeline([step1, step2])
        
        result = harden_agent_prompts([agent], pipeline)
        
        expected = "You are a very helpful assistant. Please be concise."
        assert result == {"test_agent": expected}
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_realistic_pipeline(self):
        """Test pipeline with realistic steps."""
        agent = Agent(name="assistant", llm="gpt-4", system_prompt="Help users")
        
        # Mock OpenAI response
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices[0].message.content = "You are a helpful AI assistant designed to help users with their questions."
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Create pipeline with OpenAI step
        openai_step = OpenAIGeneratorStep()
        openai_step.client = mock_client
        
        pii_step = PIIProtectionStep()
        pipeline = PromptHardeningPipeline([openai_step, pii_step])
        
        result = harden_agent_prompts([agent], pipeline)
        
        # Should have processed through both steps
        assert "assistant" in result
        assert isinstance(result["assistant"], str)
        mock_client.chat.completions.create.assert_called_once()


class TestAbstractBaseClass:
    """Test the abstract base class."""
    
    def test_prompt_hardening_step_is_abstract(self):
        """Test that PromptHardeningStep cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PromptHardeningStep()
    
    def test_subclass_must_implement_harden(self):
        """Test that subclasses must implement harden method."""
        class IncompleteStep(PromptHardeningStep):
            pass
        
        with pytest.raises(TypeError):
            IncompleteStep()
    
    def test_valid_subclass_works(self):
        """Test that valid subclass can be instantiated."""
        class ValidStep(PromptHardeningStep):
            def harden(self, system_prompt: str) -> str:
                return system_prompt
        
        step = ValidStep()
        assert step.harden("test") == "test"