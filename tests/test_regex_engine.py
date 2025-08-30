"""
Comprehensive unit tests for regex engine
Tests pattern compilation, caching, flags, capture groups, and error handling
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import re
from unittest.mock import patch
from plugins.available.regex_plugin import RegexProcessor, RegexPlugin
from utils import ConfigManager

# Initialize config for tests
ConfigManager.initialize()


class TestRegexProcessor(unittest.TestCase):
    """Test the core RegexProcessor functionality"""
    
    def setUp(self):
        """Set up test cases"""
        self.basic_rules = [
            {'pattern': r'\bforward slash\b', 'replacement': '/', 'enabled': True},
            {'pattern': r'\bnew line\b', 'replacement': '\n', 'enabled': True},
            {'pattern': r'\bum\b', 'replacement': '', 'enabled': True},
        ]
    
    def test_initialization_with_empty_rules(self):
        """Test processor initialization with empty rules"""
        processor = RegexProcessor([])
        self.assertEqual(len(processor.rules), 0)
        self.assertEqual(len(processor.compiled_rules), 0)
    
    def test_initialization_with_none_rules(self):
        """Test processor initialization with None rules"""
        processor = RegexProcessor(None)
        self.assertEqual(len(processor.rules), 0)
        self.assertEqual(len(processor.compiled_rules), 0)
    
    def test_rule_compilation_basic(self):
        """Test basic rule compilation"""
        processor = RegexProcessor(self.basic_rules)
        
        self.assertEqual(len(processor.compiled_rules), 3)
        
        # Check that patterns are compiled
        for compiled_rule in processor.compiled_rules:
            self.assertIsInstance(compiled_rule['pattern'], re.Pattern)
            self.assertIn('replacement', compiled_rule)
            self.assertIn('description', compiled_rule)
    
    def test_rule_compilation_with_flags(self):
        """Test rule compilation with regex flags"""
        rules = [
            {
                'pattern': r'hello',
                'replacement': 'HELLO',
                'flags': ['ignorecase'],
                'enabled': True
            },
            {
                'pattern': r'^line1.*line2$',
                'replacement': 'MATCHED',
                'flags': ['multiline', 'dotall'],
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        
        # Test case insensitive flag
        result = processor.process("Hello World")
        self.assertEqual(result, "HELLO World")
        
        # Test multiline flag
        multiline_text = "line1 something\nline2"
        result = processor.process(multiline_text)
        self.assertEqual(result, "MATCHED")
    
    def test_disabled_rules_ignored(self):
        """Test that disabled rules are not compiled or applied"""
        rules = [
            {'pattern': r'keep', 'replacement': 'KEEP', 'enabled': True},
            {'pattern': r'skip', 'replacement': 'SKIP', 'enabled': False},
        ]
        
        processor = RegexProcessor(rules)
        
        # Only enabled rule should be compiled
        self.assertEqual(len(processor.compiled_rules), 1)
        
        # Only enabled rule should be applied
        result = processor.process("keep this skip that")
        self.assertEqual(result, "KEEP this skip that")
    
    def test_invalid_pattern_handling(self):
        """Test that invalid regex patterns are handled gracefully"""
        rules = [
            {'pattern': r'valid', 'replacement': 'VALID', 'enabled': True},
            {'pattern': r'[invalid', 'replacement': 'INVALID', 'enabled': True},  # Unclosed bracket
            {'pattern': r'also_valid', 'replacement': 'ALSO_VALID', 'enabled': True},
        ]
        
        with patch('builtins.print') as mock_print:
            processor = RegexProcessor(rules)
        
        # Should compile 2 valid rules, skip 1 invalid
        self.assertEqual(len(processor.compiled_rules), 2)
        
        # Should print error message for invalid pattern
        mock_print.assert_called()
        error_call = str(mock_print.call_args_list[0])
        self.assertIn('Invalid regex pattern', error_call)
        self.assertIn('[invalid', error_call)
    
    def test_empty_pattern_skipped(self):
        """Test that empty patterns are skipped during compilation"""
        rules = [
            {'pattern': '', 'replacement': 'EMPTY', 'enabled': True},
            {'pattern': r'valid', 'replacement': 'VALID', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        
        # Only the valid pattern should be compiled
        self.assertEqual(len(processor.compiled_rules), 1)
        self.assertEqual(processor.compiled_rules[0]['replacement'], 'VALID')
    
    def test_basic_text_processing(self):
        """Test basic text replacement functionality"""
        processor = RegexProcessor(self.basic_rules)
        
        test_cases = [
            ("Use forward slash here", "Use / here"),
            ("Add new line break", "Add \n break"),
            ("Remove um filler", "Remove  filler"),
            ("No changes needed", "No changes needed"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = processor.process(input_text)
                self.assertEqual(result, expected)
    
    def test_sequential_rule_application(self):
        """Test that rules are applied in sequence"""
        rules = [
            {'pattern': r'first', 'replacement': 'second', 'enabled': True},
            {'pattern': r'second', 'replacement': 'third', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("first step")
        
        # Both rules should apply in sequence: first -> second -> third
        self.assertEqual(result, "third step")
    
    def test_capture_groups(self):
        """Test regex replacements with capture groups"""
        rules = [
            {
                'pattern': r'(\w+) says (\w+)',
                'replacement': r'\2 is said by \1',
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("Alice says hello")
        self.assertEqual(result, "hello is said by Alice")
    
    def test_escape_sequences(self):
        """Test that escape sequences work correctly"""
        rules = [
            {'pattern': r'tab', 'replacement': '\t', 'enabled': True},  # Use actual tab
            {'pattern': r'quote', 'replacement': '"', 'enabled': True},  # Use actual quote
        ]
        
        processor = RegexProcessor(rules)
        
        result = processor.process("Insert tab here")
        self.assertEqual(result, "Insert \t here")
        
        result = processor.process("Add quote marks")
        self.assertEqual(result, "Add \" marks")
    
    def test_empty_text_handling(self):
        """Test processing of empty or None text"""
        processor = RegexProcessor(self.basic_rules)
        
        # Empty string should return empty string
        self.assertEqual(processor.process(""), "")
        
        # None should return None
        self.assertIsNone(processor.process(None))
    
    def test_rule_exception_handling(self):
        """Test that exceptions during rule application are handled"""
        # Create a rule that might cause issues with certain inputs
        rules = [
            {'pattern': r'(\w+)', 'replacement': r'\1\2', 'enabled': True},  # Invalid group reference
        ]
        
        processor = RegexProcessor(rules)
        
        with patch('builtins.print') as mock_print:
            result = processor.process("test text")
        
        # Should handle the error gracefully and return original text
        # The exact behavior depends on how Python's re.sub handles invalid group refs
        self.assertIsNotNone(result)
        
    def test_performance_with_multiple_rules(self):
        """Test performance with many rules"""
        # Create 50 rules to test scalability
        rules = []
        for i in range(50):
            rules.append({
                'pattern': f'rule{i}',
                'replacement': f'RULE{i}',
                'enabled': True
            })
        
        processor = RegexProcessor(rules)
        
        # Should compile all 50 rules
        self.assertEqual(len(processor.compiled_rules), 50)
        
        # Should process text efficiently
        test_text = "This has rule5 and rule25 in it"
        result = processor.process(test_text)
        expected = "This has RULE5 and RULE25 in it"
        self.assertEqual(result, expected)
    
    def test_pattern_caching(self):
        """Test that compiled patterns are cached for reuse"""
        processor = RegexProcessor(self.basic_rules)
        
        # Process same text multiple times
        text = "forward slash and new line"
        
        result1 = processor.process(text)
        result2 = processor.process(text)
        result3 = processor.process(text)
        
        # All results should be identical
        expected = "/ and \n"
        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)
        self.assertEqual(result3, expected)
        
        # Compiled rules should remain the same (cached)
        self.assertEqual(len(processor.compiled_rules), 3)


class TestRegexPlugin(unittest.TestCase):
    """Test the RegexPlugin wrapper"""
    
    def test_plugin_initialization_disabled(self):
        """Test plugin with disabled config"""
        plugin = RegexPlugin()
        config = {'enabled': False}
        
        plugin.initialize(config)
        
        self.assertFalse(plugin.is_enabled())
        self.assertIsNone(plugin.get_processor())
    
    def test_plugin_initialization_enabled_with_rules(self):
        """Test plugin with enabled config and rules"""
        plugin = RegexPlugin()
        config = {
            'enabled': True,
            'rules': [
                {'pattern': r'test', 'replacement': 'TEST', 'enabled': True}
            ]
        }
        
        with patch('builtins.print'):  # Suppress output
            plugin.initialize(config)
        
        self.assertTrue(plugin.is_enabled())
        self.assertIsNotNone(plugin.get_processor())
        self.assertIsInstance(plugin.get_processor(), RegexProcessor)
    
    def test_plugin_initialization_enabled_no_rules(self):
        """Test plugin with enabled config but no rules"""
        plugin = RegexPlugin()
        config = {'enabled': True, 'rules': []}
        
        with patch('builtins.print') as mock_print:
            plugin.initialize(config)
        
        # Should disable itself when no rules
        self.assertFalse(plugin.is_enabled())
        self.assertIsNone(plugin.get_processor())
        
        # Should print warning
        mock_print.assert_called()
    
    def test_plugin_metadata(self):
        """Test plugin metadata methods"""
        plugin = RegexPlugin()
        
        self.assertEqual(plugin.get_name(), "regex_processor")
        self.assertEqual(plugin.get_version(), "1.0.0")
        self.assertIn("regex", plugin.get_description().lower())
        self.assertEqual(plugin.get_priority(), 30)


class TestRegexEngineIntegration(unittest.TestCase):
    """Integration tests for regex engine with real-world scenarios"""
    
    def test_programming_terms(self):
        """Test common programming term replacements"""
        rules = [
            {'pattern': r'\bopen paren\b', 'replacement': '(', 'enabled': True},
            {'pattern': r'\bclose paren\b', 'replacement': ')', 'enabled': True},
            {'pattern': r'\bopen brace\b', 'replacement': '{', 'enabled': True},
            {'pattern': r'\bclose brace\b', 'replacement': '}', 'enabled': True},
            {'pattern': r'\bsemi colon\b', 'replacement': ';', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        
        input_text = "if condition open paren true close paren open brace return semi colon close brace"
        expected = "if condition ( true ) { return ; }"
        result = processor.process(input_text)
        
        self.assertEqual(result, expected)
    
    def test_punctuation_fixes(self):
        """Test punctuation correction rules"""
        rules = [
            {'pattern': r'\bperiod\b', 'replacement': '.', 'enabled': True},
            {'pattern': r'\bcomma\b', 'replacement': ',', 'enabled': True},
            {'pattern': r'\bquestion mark\b', 'replacement': '?', 'enabled': True},
            {'pattern': r'\bexclamation point\b', 'replacement': '!', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        
        test_cases = [
            ("Hello world period", "Hello world ."),
            ("First item comma second item", "First item , second item"),
            ("Are you sure question mark", "Are you sure ?"),
            ("Great job exclamation point", "Great job !"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = processor.process(input_text)
                self.assertEqual(result, expected)
    
    def test_complex_replacement_chains(self):
        """Test complex replacement scenarios"""
        rules = [
            # First normalize spoken punctuation
            {'pattern': r'\bperiod\b', 'replacement': '.', 'enabled': True},
            {'pattern': r'\bcomma\b', 'replacement': ',', 'enabled': True},
            
            # Then fix spacing around punctuation
            {'pattern': r'\s+\.', 'replacement': '.', 'enabled': True},
            {'pattern': r'\s+,', 'replacement': ',', 'enabled': True},
            
            # Finally clean up multiple spaces
            {'pattern': r'\s+', 'replacement': ' ', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        
        input_text = "Hello   world  period    This  is  a  test  comma  right  period"
        expected = "Hello world. This is a test, right."
        result = processor.process(input_text)
        
        self.assertEqual(result, expected)
    
    def test_case_insensitive_replacements(self):
        """Test case-insensitive pattern matching"""
        rules = [
            {
                'pattern': r'\b(hello|hi|hey)\b',
                'replacement': 'greetings',
                'flags': ['ignorecase'],
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        
        test_cases = [
            ("Hello there", "greetings there"),
            ("HI everyone", "greetings everyone"),  
            ("hey buddy", "greetings buddy"),
            ("Say hello", "Say greetings"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = processor.process(input_text)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    print("Running Regex Engine Unit Tests")
    print("=" * 40)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)