"""
Tests for advanced regex processor features
Tests performance tracking, priorities, conditional rules, and validation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch
from plugins.available.regex_plugin import RegexProcessor, RegexPlugin
from plugins.available.regex_templates import (
    get_template_categories, get_template, get_template_rules,
    create_combined_template, get_common_combinations, export_template_to_config
)
from utils import ConfigManager

# Initialize config for tests
ConfigManager.initialize()


class TestAdvancedRegexFeatures(unittest.TestCase):
    """Test advanced regex processor features"""
    
    def test_rule_priorities(self):
        """Test that rules are applied in priority order"""
        rules = [
            {'pattern': r'test', 'replacement': 'HIGH', 'priority': 10, 'enabled': True},
            {'pattern': r'HIGH', 'replacement': 'FINAL', 'priority': 20, 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("test word")
        
        # Lower priority numbers execute first: test -> HIGH -> FINAL
        self.assertEqual(result, "FINAL word")
    
    def test_performance_tracking(self):
        """Test that performance statistics are tracked"""
        rules = [
            {'pattern': r'track', 'replacement': 'TRACKED', 'enabled': True},
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
    
    def test_performance_tracking_disable(self):
        """Test disabling performance tracking"""
        rules = [
            {'pattern': r'test', 'replacement': 'TEST', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        processor.disable_performance_tracking()
        
        # Process text
        processor.process("test word")
        
        stats = processor.get_rule_statistics()
        rule_stats = list(stats.values())[0]
        
        # Stats should not be updated when tracking is disabled
        self.assertEqual(rule_stats['matches'], 0)
        self.assertEqual(rule_stats['total_time'], 0.0)
    
    def test_reset_statistics(self):
        """Test resetting performance statistics"""
        rules = [
            {'pattern': r'reset', 'replacement': 'RESET', 'enabled': True},
        ]
        
        processor = RegexProcessor(rules)
        
        # Process to generate stats
        processor.process("reset test")
        
        # Verify stats exist
        stats = processor.get_rule_statistics()
        rule_stats = list(stats.values())[0]
        self.assertGreater(rule_stats['matches'], 0)
        
        # Reset stats
        processor.reset_statistics()
        
        # Verify stats are reset
        stats = processor.get_rule_statistics()
        rule_stats = list(stats.values())[0]
        self.assertEqual(rule_stats['matches'], 0)
        self.assertEqual(rule_stats['total_time'], 0.0)
    
    def test_conditional_rules(self):
        """Test conditional rule application"""
        rules = [
            {
                'pattern': r'conditional',
                'replacement': 'APPLIED',
                'enabled': True,
                'conditions': {
                    'context_values': {'mode': 'test', 'enabled': True}
                }
            },
            {
                'pattern': r'always',
                'replacement': 'ALWAYS',
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        
        # Test without matching context
        result = processor.process("conditional and always", {})
        self.assertEqual(result, "conditional and ALWAYS")
        
        # Test with non-matching context
        result = processor.process("conditional and always", {'mode': 'other'})
        self.assertEqual(result, "conditional and ALWAYS")
        
        # Test with matching context
        result = processor.process("conditional and always", {'mode': 'test', 'enabled': True})
        self.assertEqual(result, "APPLIED and ALWAYS")
    
    def test_conditional_rules_context_contains(self):
        """Test conditional rules with context_contains"""
        rules = [
            {
                'pattern': r'need_keys',
                'replacement': 'MATCHED',
                'enabled': True,
                'conditions': {
                    'context_contains': ['key1', 'key2']
                }
            }
        ]
        
        processor = RegexProcessor(rules)
        
        # Test without required keys
        result = processor.process("need_keys here", {'key1': 'value1'})
        self.assertEqual(result, "need_keys here")  # No match
        
        # Test with all required keys
        result = processor.process("need_keys here", {'key1': 'value1', 'key2': 'value2'})
        self.assertEqual(result, "MATCHED here")  # Match
    
    def test_additional_regex_flags(self):
        """Test additional regex flags (verbose, ascii)"""
        rules = [
            {
                'pattern': r'''(?x)  # Verbose mode
                                \b    # Word boundary
                                test  # Literal "test"
                                \b    # Word boundary
                              ''',
                'replacement': 'VERBOSE',
                'flags': ['verbose'],
                'enabled': True
            }
        ]
        
        processor = RegexProcessor(rules)
        result = processor.process("test this")
        self.assertEqual(result, "VERBOSE this")


class TestRegexValidation(unittest.TestCase):
    """Test regex pattern validation methods"""
    
    def test_validate_pattern_valid(self):
        """Test validation of valid patterns"""
        processor = RegexProcessor([])
        
        is_valid, message = processor.validate_pattern(r'\btest\b', is_regex=True)
        self.assertTrue(is_valid)
        self.assertIn("valid", message.lower())
    
    def test_validate_pattern_invalid(self):
        """Test validation of invalid patterns"""
        processor = RegexProcessor([])
        
        is_valid, message = processor.validate_pattern(r'[invalid', is_regex=True)
        self.assertFalse(is_valid)
        self.assertIn("invalid", message.lower())
    
    def test_validate_pattern_empty(self):
        """Test validation of empty pattern"""
        processor = RegexProcessor([])
        
        is_valid, message = processor.validate_pattern('', is_regex=True)
        self.assertFalse(is_valid)
        self.assertIn("empty", message.lower())
    
    def test_validate_pattern_with_flags(self):
        """Test validation with regex flags"""
        processor = RegexProcessor([])
        
        is_valid, message = processor.validate_pattern(r'test', is_regex=True, flags=['ignorecase'])
        self.assertTrue(is_valid)
        
        is_valid, message = processor.validate_pattern(r'test', is_regex=True, flags=['invalid_flag'])
        self.assertFalse(is_valid)
        self.assertIn("Unknown flag", message)
    
    def test_test_rule_valid(self):
        """Test the test_rule method with valid input"""
        processor = RegexProcessor([])
        
        result = processor.test_rule(r'\btest\b', 'TEST', 'test this test')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['original'], 'test this test')
        self.assertEqual(result['result'], 'TEST this TEST')
        self.assertEqual(result['matches'], 2)
        self.assertTrue(result['changed'])
        self.assertGreater(result['execution_time'], 0)
        self.assertEqual(len(result['match_details']), 2)
    
    def test_test_rule_invalid(self):
        """Test the test_rule method with invalid pattern"""
        processor = RegexProcessor([])
        
        result = processor.test_rule(r'[invalid', 'REPLACEMENT', 'test text')
        
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertEqual(result['original'], 'test text')
        self.assertEqual(result['result'], 'test text')
        self.assertEqual(result['matches'], 0)
    
    def test_test_rule_no_matches(self):
        """Test the test_rule method with no matches"""
        processor = RegexProcessor([])
        
        result = processor.test_rule(r'nomatch', 'REPLACEMENT', 'test text')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['matches'], 0)
        self.assertFalse(result['changed'])
        self.assertEqual(result['original'], result['result'])


class TestRegexTemplates(unittest.TestCase):
    """Test the regex templates system"""
    
    def test_get_template_categories(self):
        """Test getting list of template categories"""
        categories = get_template_categories()
        
        self.assertIsInstance(categories, list)
        self.assertIn('punctuation', categories)
        self.assertIn('programming', categories)
        self.assertIn('speech_cleanup', categories)
    
    def test_get_template(self):
        """Test getting a specific template"""
        template = get_template('punctuation')
        
        self.assertIsInstance(template, dict)
        self.assertIn('name', template)
        self.assertIn('description', template)
        self.assertIn('rules', template)
        self.assertIsInstance(template['rules'], list)
    
    def test_get_template_nonexistent(self):
        """Test getting non-existent template"""
        template = get_template('nonexistent')
        self.assertEqual(template, {})
    
    def test_get_template_rules(self):
        """Test getting rules from a template"""
        rules = get_template_rules('punctuation')
        
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        
        # Check first rule structure
        first_rule = rules[0]
        self.assertIn('pattern', first_rule)
        self.assertIn('replacement', first_rule)
        self.assertIn('description', first_rule)
        self.assertIn('enabled', first_rule)
    
    def test_create_combined_template(self):
        """Test combining multiple templates"""
        combined = create_combined_template(['punctuation', 'programming'])
        
        self.assertIn('name', combined)
        self.assertIn('description', combined)
        self.assertIn('rules', combined)
        self.assertIn('categories', combined)
        
        # Should have rules from both categories
        self.assertGreater(len(combined['rules']), 0)
        
        # Rules should be sorted by priority
        priorities = [rule.get('priority', 50) for rule in combined['rules']]
        self.assertEqual(priorities, sorted(priorities))
    
    def test_get_common_combinations(self):
        """Test getting pre-defined template combinations"""
        combinations = get_common_combinations()
        
        self.assertIsInstance(combinations, dict)
        self.assertIn('basic', combinations)
        self.assertIn('programming', combinations)
        
        # Check basic combination
        basic = combinations['basic']
        self.assertIn('rules', basic)
        self.assertGreater(len(basic['rules']), 0)
    
    def test_export_template_to_config(self):
        """Test exporting template to config format"""
        template = get_template('punctuation')
        config_format = export_template_to_config(template)
        
        self.assertIn('enabled', config_format)
        self.assertIn('rules', config_format)
        self.assertTrue(config_format['enabled'])
        self.assertEqual(config_format['rules'], template['rules'])
    
    def test_template_with_processor(self):
        """Test using template rules with RegexProcessor"""
        rules = get_template_rules('punctuation')
        processor = RegexProcessor(rules)
        
        # Test that template rules work
        result = processor.process("Hello period How are you question mark")
        self.assertEqual(result, "Hello . How are you ?")


class TestRegexIntegrationWithTemplates(unittest.TestCase):
    """Integration tests using templates with the regex processor"""
    
    def test_programming_template(self):
        """Test using programming template for code dictation"""
        rules = get_template_rules('programming')
        processor = RegexProcessor(rules)
        
        input_text = "if condition open paren x equals five close paren open brace return true semicolon close brace"
        result = processor.process(input_text)
        
        # Check that programming symbols are converted
        self.assertIn('(', result)
        self.assertIn(')', result)
        self.assertIn('{', result)
        self.assertIn('}', result)
        self.assertIn('=', result)
        self.assertIn(';', result)
    
    def test_combined_speech_cleanup(self):
        """Test combined speech cleanup and punctuation template"""
        combination = get_common_combinations()['basic']
        processor = RegexProcessor(combination['rules'])
        
        input_text = "Um hello world period This is um a test comma right question mark"
        result = processor.process(input_text)
        
        # Should remove "um" and convert punctuation
        self.assertNotIn('um', result.lower())
        self.assertIn('.', result)
        self.assertIn(',', result)
        self.assertIn('?', result)
    
    def test_priority_ordering_in_templates(self):
        """Test that template rules respect priority ordering"""
        # Get rules that should run in specific order
        rules = get_template_rules('speech_cleanup')
        processor = RegexProcessor(rules)
        
        # The whitespace normalization should run after filler word removal
        input_text = "Hello  um   world   uh   test"
        result = processor.process(input_text)
        
        # Should not have "um" or "uh", and should have normalized spaces
        self.assertNotIn('um', result)
        self.assertNotIn('uh', result)
        # Should not have multiple consecutive spaces
        self.assertNotIn('   ', result)
        self.assertNotIn('  ', result)


if __name__ == '__main__':
    print("Running Advanced Regex Feature Tests")
    print("=" * 45)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)