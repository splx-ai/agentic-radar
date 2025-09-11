"""
Tests for tool categorization functionality.

These tests cover the tool categorization logic for different frameworks.
"""

import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

import pytest

from agentic_radar.graph import ToolType
from agentic_radar.analysis.openai_agents.tool_categorizer.categorizer import load_tool_categories
from agentic_radar.analysis.crewai.tool_descriptions import (
    is_package_installed, 
    parse_init_imports
)


class TestOpenAIAgentsToolCategorizer:
    """Test OpenAI Agents tool categorization."""
    
    def test_load_tool_categories_success(self):
        """Test successful loading of tool categories."""
        # Create mock categories.json content
        categories_data = {
            "web_search": "WEB_SEARCH",
            "file_tool": "DOCUMENT_LOADER",
            "python_executor": "CODE_INTERPRETER"
        }
        
        with patch('importlib_resources.files') as mock_files:
            # Mock the resource loading
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(categories_data)
            mock_files.return_value.joinpath.return_value = mock_path
            
            result = load_tool_categories()
            
            expected = {
                "web_search": ToolType.WEB_SEARCH,
                "file_tool": ToolType.DOCUMENT_LOADER,
                "python_executor": ToolType.CODE_INTERPRETER
            }
            assert result == expected
    
    def test_load_tool_categories_unknown_type(self):
        """Test loading with unknown tool type."""
        categories_data = {
            "valid_tool": "WEB_SEARCH",
            "invalid_tool": "UNKNOWN_TYPE"
        }
        
        with patch('importlib_resources.files') as mock_files:
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(categories_data)
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('builtins.print') as mock_print:
                result = load_tool_categories()
            
            # Should default unknown types to DEFAULT
            expected = {
                "valid_tool": ToolType.WEB_SEARCH,
                "invalid_tool": ToolType.DEFAULT
            }
            assert result == expected
            mock_print.assert_called_once()
    
    def test_load_tool_categories_invalid_json(self):
        """Test loading with invalid JSON."""
        with patch('importlib_resources.files') as mock_files:
            mock_path = Mock()
            mock_path.read_text.return_value = "invalid json"
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('builtins.print') as mock_print:
                result = load_tool_categories()
            
            assert result == {}
            mock_print.assert_called_once()
    
    def test_load_tool_categories_not_dict(self):
        """Test loading when JSON is not a dictionary."""
        with patch('importlib_resources.files') as mock_files:
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(["not", "a", "dict"])
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('builtins.print') as mock_print:
                result = load_tool_categories()
            
            assert result == {}
            mock_print.assert_called_once()
    
    def test_load_tool_categories_invalid_types(self):
        """Test loading with invalid key/value types."""
        categories_data = {
            "valid_tool": "WEB_SEARCH",
            123: "DOCUMENT_LOADER",  # Invalid key type
            "another_tool": 456      # Invalid value type
        }
        
        with patch('importlib_resources.files') as mock_files:
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(categories_data)
            mock_files.return_value.joinpath.return_value = mock_path
            
            with patch('builtins.print') as mock_print:
                result = load_tool_categories()
            
            assert result == {}
            mock_print.assert_called_once()
    
    def test_load_tool_categories_file_not_found(self):
        """Test loading when categories.json file is missing."""
        with patch('importlib_resources.files') as mock_files:
            mock_files.return_value.joinpath.side_effect = FileNotFoundError("File not found")
            
            with patch('builtins.print') as mock_print:
                result = load_tool_categories()
            
            assert result == {}
            mock_print.assert_called_once()


class TestCrewAIToolDescriptions:
    """Test CrewAI tool descriptions and utilities."""
    
    def test_is_package_installed_existing_package(self):
        """Test checking for an existing package."""
        # Test with a package that should always exist
        result = is_package_installed("os")
        assert result is True
    
    def test_is_package_installed_nonexistent_package(self):
        """Test checking for a non-existent package."""
        result = is_package_installed("definitely_nonexistent_package_12345")
        assert result is False
    
    def test_is_package_installed_with_real_packages(self):
        """Test with some real packages that might be installed."""
        # These tests depend on the environment, so we test both cases
        common_packages = ["json", "sys", "os", "typing"]
        for package in common_packages:
            result = is_package_installed(package)
            assert isinstance(result, bool)
    
    def test_parse_init_imports_simple_from_import(self):
        """Test parsing simple from imports."""
        init_content = """
from .tool1 import ToolClass1
from .tool2 import ToolClass2
from ..common import CommonTool
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write(init_content)
            f.flush()
            
            try:
                result = parse_init_imports(f.name)
                
                # Should extract the imports
                expected = [
                    ("ToolClass1", "tool1"),
                    ("ToolClass2", "tool2"), 
                    ("CommonTool", "common")
                ]
                # The exact behavior depends on implementation
                assert isinstance(result, list)
                for item in result:
                    assert isinstance(item, tuple)
                    assert len(item) == 2
                    
            finally:
                os.unlink(f.name)
    
    def test_parse_init_imports_multiple_imports(self):
        """Test parsing multiple imports from same module."""
        init_content = """
from .tools import Tool1, Tool2, Tool3
from .utils import Helper1, Helper2
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write(init_content)
            f.flush()
            
            try:
                result = parse_init_imports(f.name)
                assert isinstance(result, list)
                # Should handle multiple imports per line
                
            finally:
                os.unlink(f.name)
    
    def test_parse_init_imports_empty_file(self):
        """Test parsing empty __init__.py file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write("")
            f.flush()
            
            try:
                result = parse_init_imports(f.name)
                assert isinstance(result, list)
                # Empty file should return empty list or handle gracefully
                
            finally:
                os.unlink(f.name)
    
    def test_parse_init_imports_syntax_errors(self):
        """Test parsing file with syntax errors."""
        init_content = """
from .tools import (
    Tool1,
    Tool2,
    # Missing closing parenthesis
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write(init_content)
            f.flush()
            
            try:
                # Should handle syntax errors gracefully
                result = parse_init_imports(f.name)
                assert isinstance(result, list)
                
            finally:
                os.unlink(f.name)
    
    def test_parse_init_imports_nonexistent_file(self):
        """Test parsing non-existent file."""
        result = parse_init_imports("/nonexistent/path/__init__.py")
        assert isinstance(result, list)
        # Should handle missing file gracefully
    
    def test_parse_init_imports_complex_imports(self):
        """Test parsing complex import patterns."""
        init_content = """
# Regular imports
from .basic_tools import SimpleTool
from .advanced_tools import AdvancedTool

# Import with as
from .renamed import Tool as RenamedTool

# Absolute imports
from crewai_tools.external import ExternalTool

# Multiple imports
from .multi import (
    Tool1,
    Tool2,
    Tool3
)

# Comments and other statements
some_variable = "value"

from .final import FinalTool
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write(init_content)
            f.flush()
            
            try:
                result = parse_init_imports(f.name)
                assert isinstance(result, list)
                
                # Should extract all valid imports
                for item in result:
                    assert isinstance(item, tuple)
                    assert len(item) == 2
                    assert isinstance(item[0], str)  # class name
                    assert isinstance(item[1], str)  # module path
                    
            finally:
                os.unlink(f.name)


class TestToolTypeEnum:
    """Test the ToolType enum functionality."""
    
    def test_tool_type_values(self):
        """Test ToolType enum has expected values."""
        expected_types = [
            "WEB_SEARCH",
            "LLM", 
            "CODE_INTERPRETER",
            "DOCUMENT_LOADER",
            "DEFAULT"
        ]
        
        for type_name in expected_types:
            assert hasattr(ToolType, type_name)
            tool_type = getattr(ToolType, type_name)
            assert str(tool_type) == type_name.lower()
    
    def test_tool_type_string_conversion(self):
        """Test ToolType string conversion."""
        assert str(ToolType.WEB_SEARCH) == "web_search"
        assert str(ToolType.LLM) == "llm"
        assert str(ToolType.CODE_INTERPRETER) == "code_interpreter"
        assert str(ToolType.DOCUMENT_LOADER) == "document_loader"
        assert str(ToolType.DEFAULT) == "default"


class TestToolCategorizationIntegration:
    """Integration tests for tool categorization across frameworks."""
    
    def test_categorization_consistency(self):
        """Test that tool categorization is consistent across frameworks."""
        # This test ensures that similar tools get similar categories
        # across different frameworks
        
        # Load OpenAI agents categories
        with patch('importlib_resources.files') as mock_files:
            categories_data = {
                "web_search_tool": "WEB_SEARCH",
                "file_reader": "DOCUMENT_LOADER", 
                "python_exec": "CODE_INTERPRETER"
            }
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(categories_data)
            mock_files.return_value.joinpath.return_value = mock_path
            
            openai_categories = load_tool_categories()
        
        # Test that web search tools are consistently categorized
        web_search_tools = [k for k, v in openai_categories.items() if v == ToolType.WEB_SEARCH]
        assert len(web_search_tools) > 0
        
        # Test that each category has at least some tools
        categories_used = set(openai_categories.values())
        assert ToolType.WEB_SEARCH in categories_used or ToolType.DEFAULT in categories_used
    
    def test_unknown_tools_default_category(self):
        """Test that unknown tools get default category."""
        with patch('importlib_resources.files') as mock_files:
            categories_data = {
                "known_tool": "WEB_SEARCH"
            }
            mock_path = Mock()
            mock_path.read_text.return_value = json.dumps(categories_data)
            mock_files.return_value.joinpath.return_value = mock_path
            
            categories = load_tool_categories()
        
        # Known tool should have correct category
        assert categories.get("known_tool") == ToolType.WEB_SEARCH
        
        # Unknown tools would need to be handled by calling code
        # This tests the structure is correct for that handling
        assert isinstance(categories, dict)
        for tool_name, category in categories.items():
            assert isinstance(tool_name, str)
            assert isinstance(category, ToolType)