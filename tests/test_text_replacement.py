"""
Tests for plain text replacement functionality
Tests both regex and text replacements working together
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from plugins.available.regex_plugin import RegexProcessor
from plugins.available.regex_templates import get_template_rules, get_common_combinations
from utils import ConfigManager

# Initialize config for tests
ConfigManager.initialize()


class TestTextReplacement(unittest.TestCase):
    """Test plain text replacement functionality"""
    
    def test_simple_text_replacement(self):
        """Test basic text replacement without regex"""
        rules = [
            {
                'pattern': 'hello',
                'replacement': 'hi',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("hello world hello again")
        self.assertEqual(result, "hi world hi again")
    
    def test_case_insensitive_text_replacement(self):
        """Test case-insensitive text replacement"""
        rules = [
            {
                'pattern': 'hello',
                'replacement': 'hi',
                'is_regex': False,
                'flags': ['ignorecase'],
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("Hello WORLD hello Again")
        self.assertEqual(result, "hi WORLD hi Again")
    
    def test_case_sensitive_text_replacement(self):
        """Test case-sensitive text replacement (default)"""
        rules = [
            {
                'pattern': 'hello',
                'replacement': 'hi',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("Hello world hello again")
        self.assertEqual(result, "Hello world hi again")  # Only lowercase matches
    
    def test_text_replacement_with_special_characters(self):
        """Test text replacement with regex special characters"""
        rules = [
            {
                'pattern': 'file.txt',  # Contains regex special character '.'
                'replacement': 'document.docx',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("Open file.txt please")
        self.assertEqual(result, "Open document.docx please")
    
    def test_mixed_regex_and_text_rules(self):
        """Test processor with both regex and text replacement rules"""
        rules = [
            {
                'pattern': r'\btest\b',  # Regex rule
                'replacement': 'TEST',
                'is_regex': True,
                'priority': 10,
                'enabled': True
            },
            {
                'pattern': 'hello world',  # Text rule
                'replacement': 'hi earth',
                'is_regex': False,
                'priority': 20,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("test hello world test")
        
        # Should apply in priority order: test->TEST first, then hello world->hi earth
        self.assertEqual(result, "TEST hi earth TEST")
    
    def test_text_replacement_performance_tracking(self):
        """Test that performance tracking works for text replacements"""
        rules = [
            {
                'pattern': 'track',
                'replacement': 'TRACKED',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        
        # Process text multiple times
        processor.process("track this")
        processor.process("track that")
        processor.process("no match")
        
        stats = processor.get_rule_statistics()
        
        # Should have one rule
        self.assertEqual(len(stats), 1)
        
        # Get the rule stats
        rule_stats = list(stats.values())[0]
        
        # Should have recorded 2 matches
        self.assertEqual(rule_stats['matches'], 2)
        self.assertGreater(rule_stats['total_time'], 0)
        self.assertGreater(rule_stats['avg_time'], 0)


class TestTextValidationAndTesting(unittest.TestCase):
    """Test validation and testing methods for text replacements"""
    
    def test_validate_text_pattern(self):
        """Test validation of text patterns"""
        processor = RegexProcessor([])
        
        # Text patterns should always be valid
        is_valid, message = processor.validate_pattern("any text", is_regex=False)
        self.assertTrue(is_valid)
        self.assertIn("valid", message.lower())
    
    def test_validate_empty_text_pattern(self):
        """Test validation of empty text pattern"""
        processor = RegexProcessor([])
        
        is_valid, message = processor.validate_pattern("", is_regex=False)
        self.assertFalse(is_valid)
        self.assertIn("empty", message.lower())
    
    def test_test_text_rule_basic(self):
        """Test the test_rule method with text replacement"""
        processor = RegexProcessor([])
        
        result = processor.test_rule("hello", "hi", "hello world hello", is_regex=False)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['type'], 'text')
        self.assertEqual(result['original'], 'hello world hello')
        self.assertEqual(result['result'], 'hi world hi')
        self.assertEqual(result['matches'], 2)
        self.assertTrue(result['changed'])
        self.assertGreater(result['execution_time'], 0)
    
    def test_test_text_rule_case_insensitive(self):
        """Test the test_rule method with case-insensitive text replacement"""
        processor = RegexProcessor([])
        
        result = processor.test_rule(
            "hello", "hi", "Hello HELLO hello", 
            is_regex=False, flags=['ignorecase']
        )
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['result'], 'hi hi hi')
        self.assertEqual(result['matches'], 3)
    
    def test_test_text_rule_no_matches(self):
        """Test the test_rule method with no matches"""
        processor = RegexProcessor([])
        
        result = processor.test_rule("xyz", "ABC", "hello world", is_regex=False)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['matches'], 0)
        self.assertFalse(result['changed'])
        self.assertEqual(result['original'], result['result'])


class TestSimpleReplacementTemplates(unittest.TestCase):
    """Test the simple replacement templates"""
    
    def test_simple_replacements_template(self):
        """Test using the simple_replacements template"""
        rules = get_template_rules('simple_replacements')
        processor = RegexProcessor(rules)
        
        test_cases = [
            ("Use forward slash here", "Use / here"),
            ("Add at sign before username", "Add @ before username"),
            ("Hash tag trending", "# trending"),
            ("Dollar sign amount", "$ amount"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = processor.process(input_text)
                self.assertEqual(result, expected)
    
    def test_simple_mode_combination(self):
        """Test the simple mode template combination"""
        combination = get_common_combinations()['simple']
        processor = RegexProcessor(combination['rules'])
        
        # Should remove filler words and do simple replacements
        input_text = "Um please use forward slash and at sign"
        result = processor.process(input_text)
        
        # Should remove "Um" and convert symbols
        self.assertNotIn('Um', result)
        self.assertIn('/', result)
        self.assertIn('@', result)
    
    def test_mixed_regex_and_simple_rules(self):
        """Test that regex and simple rules work together in templates"""
        # Get rules that mix both types
        regex_rules = get_template_rules('speech_cleanup')  # These use regex
        simple_rules = get_template_rules('simple_replacements')  # These use text
        
        all_rules = regex_rules + simple_rules
        processor = RegexProcessor(all_rules)
        
        input_text = "Um forward slash and uh at sign"
        result = processor.process(input_text)
        
        # Should handle both filler word removal (regex) and symbol replacement (text)
        self.assertNotIn('Um', result)
        self.assertNotIn('uh', result)
        self.assertIn('/', result)
        self.assertIn('@', result)


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing regex rules still work (backward compatibility)"""
    
    def test_existing_regex_rules_still_work(self):
        """Test that rules without is_regex flag default to regex behavior"""
        rules = [
            {
                'pattern': r'\btest\b',
                'replacement': 'TEST',
                # No is_regex specified - should default to True
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("test word testing")
        
        # Should only replace whole word "test", not "testing"
        self.assertEqual(result, "TEST word testing")
    
    def test_existing_templates_still_work(self):
        """Test that existing templates without is_regex still function"""
        # Get a template that uses regex patterns
        rules = get_template_rules('punctuation')
        processor = RegexProcessor(rules)
        
        result = processor.process("Hello period How are you question mark")
        self.assertEqual(result, "Hello . How are you ?")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases for text replacement"""
    
    def test_empty_replacement_text(self):
        """Test text replacement with empty replacement"""
        rules = [
            {
                'pattern': 'remove',
                'replacement': '',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("please remove this remove")
        self.assertEqual(result, "please  this ")
    
    def test_overlapping_patterns(self):
        """Test text replacement with overlapping patterns"""
        rules = [
            {
                'pattern': 'hello',
                'replacement': 'hi',
                'is_regex': False,
                'priority': 10,
                'enabled': True
            },
            {
                'pattern': 'hello world',
                'replacement': 'hi earth',
                'is_regex': False,
                'priority': 20,  # Lower priority, runs after
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("hello world")
        
        # First rule runs: "hello world" -> "hi world"
        # Second rule runs: "hi world" != "hello world", so no match
        self.assertEqual(result, "hi world")
    
    def test_unicode_text_replacement(self):
        """Test text replacement with Unicode characters"""
        rules = [
            {
                'pattern': 'café',
                'replacement': 'coffee',
                'is_regex': False,
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("I love café")
        self.assertEqual(result, "I love coffee")


if __name__ == '__main__':
    print("Running Text Replacement Tests")
    print("=" * 35)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)