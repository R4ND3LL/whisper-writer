"""
Tests for regex configuration management
Tests ConfigManager extensions for regex rules
"""
import sys
import os
import tempfile
import json
import yaml
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch, mock_open
from utils import ConfigManager

class TestRegexConfig(unittest.TestCase):
    """Test regex configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        # Initialize ConfigManager
        ConfigManager.initialize()
        
        # Start with empty rules
        ConfigManager.set_regex_rules([])
    
    def test_get_empty_rules(self):
        """Test getting rules when none are configured"""
        rules = ConfigManager.get_regex_rules()
        self.assertEqual(rules, [])
    
    def test_set_and_get_rules(self):
        """Test setting and getting regex rules"""
        test_rules = [
            {
                'pattern': 'test',
                'replacement': 'TEST',
                'enabled': True,
                'is_regex': False
            }
        ]
        
        ConfigManager.set_regex_rules(test_rules)
        retrieved_rules = ConfigManager.get_regex_rules()
        
        self.assertEqual(retrieved_rules, test_rules)
    
    def test_add_regex_rule_basic(self):
        """Test adding a basic regex rule"""
        rule = ConfigManager.add_regex_rule(
            pattern='hello',
            replacement='hi',
            description='Replace hello with hi'
        )
        
        expected = {
            'pattern': 'hello',
            'replacement': 'hi',
            'description': 'Replace hello with hi',
            'enabled': True,
            'is_regex': True,
            'priority': 50
        }
        
        self.assertEqual(rule, expected)
        
        rules = ConfigManager.get_regex_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0], expected)
    
    def test_add_text_rule(self):
        """Test adding a plain text replacement rule"""
        rule = ConfigManager.add_regex_rule(
            pattern='forward slash',
            replacement='/',
            description='Replace forward slash with /',
            is_regex=False,
            flags=['ignorecase'],
            priority=20
        )
        
        expected = {
            'pattern': 'forward slash',
            'replacement': '/',
            'description': 'Replace forward slash with /',
            'enabled': True,
            'is_regex': False,
            'flags': ['ignorecase'],
            'priority': 20
        }
        
        self.assertEqual(rule, expected)
    
    def test_remove_regex_rule(self):
        """Test removing a regex rule by index"""
        # Add two rules
        ConfigManager.add_regex_rule('rule1', 'RULE1')
        ConfigManager.add_regex_rule('rule2', 'RULE2')
        
        rules = ConfigManager.get_regex_rules()
        self.assertEqual(len(rules), 2)
        
        # Remove first rule
        removed_rule = ConfigManager.remove_regex_rule(0)
        self.assertEqual(removed_rule['pattern'], 'rule1')
        
        # Check remaining rules
        rules = ConfigManager.get_regex_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['pattern'], 'rule2')
    
    def test_remove_invalid_index(self):
        """Test removing rule with invalid index"""
        ConfigManager.add_regex_rule('test', 'TEST')
        
        with self.assertRaises(IndexError):
            ConfigManager.remove_regex_rule(1)  # Out of range
        
        with self.assertRaises(IndexError):
            ConfigManager.remove_regex_rule(-1)  # Negative index
    
    def test_update_regex_rule(self):
        """Test updating a regex rule"""
        ConfigManager.add_regex_rule('original', 'ORIGINAL')
        
        updated_rule = ConfigManager.update_regex_rule(0, 
            pattern='updated',
            replacement='UPDATED',
            description='Updated rule'
        )
        
        self.assertEqual(updated_rule['pattern'], 'updated')
        self.assertEqual(updated_rule['replacement'], 'UPDATED')
        self.assertEqual(updated_rule['description'], 'Updated rule')
        
        # Verify in config
        rules = ConfigManager.get_regex_rules()
        self.assertEqual(rules[0]['pattern'], 'updated')
    
    def test_update_invalid_index(self):
        """Test updating rule with invalid index"""
        with self.assertRaises(IndexError):
            ConfigManager.update_regex_rule(0, pattern='test')
    
    def test_processor_enabled_toggle(self):
        """Test enabling/disabling regex processor"""
        # Test default state
        enabled = ConfigManager.get_regex_processor_enabled()
        # Should be True based on current config, but let's test both states
        
        # Set to false
        ConfigManager.set_regex_processor_enabled(False)
        self.assertFalse(ConfigManager.get_regex_processor_enabled())
        
        # Set to true
        ConfigManager.set_regex_processor_enabled(True)
        self.assertTrue(ConfigManager.get_regex_processor_enabled())


class TestRegexRuleValidation(unittest.TestCase):
    """Test regex rule validation"""
    
    def setUp(self):
        """Set up test environment"""
        ConfigManager.initialize()
    
    def test_validate_valid_rules(self):
        """Test validation of valid rules"""
        valid_rules = [
            {
                'pattern': 'test',
                'replacement': 'TEST',
                'enabled': True,
                'is_regex': False,
                'priority': 10,
                'flags': ['ignorecase']
            },
            {
                'pattern': r'\bword\b',
                'replacement': 'WORD'
            }
        ]
        
        is_valid, errors = ConfigManager.validate_regex_rules(valid_rules)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
    
    def test_validate_invalid_structure(self):
        """Test validation of invalid rule structure"""
        # Not a list
        is_valid, errors = ConfigManager.validate_regex_rules("not a list")
        self.assertFalse(is_valid)
        self.assertIn("must be a list", errors[0])
        
        # Not a dict
        is_valid, errors = ConfigManager.validate_regex_rules(["not a dict"])
        self.assertFalse(is_valid)
        self.assertIn("Must be an object", errors[0])
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields"""
        # Missing pattern
        rules = [{'replacement': 'TEST'}]
        is_valid, errors = ConfigManager.validate_regex_rules(rules)
        self.assertFalse(is_valid)
        self.assertIn("Missing required 'pattern'", errors[0])
        
        # Missing replacement
        rules = [{'pattern': 'test'}]
        is_valid, errors = ConfigManager.validate_regex_rules(rules)
        self.assertFalse(is_valid)
        self.assertIn("Missing required 'replacement'", errors[0])
    
    def test_validate_wrong_types(self):
        """Test validation with wrong field types"""
        rules = [
            {
                'pattern': 123,  # Should be string
                'replacement': [],  # Should be string
                'enabled': 'yes',  # Should be boolean
                'is_regex': 1,  # Should be boolean
                'priority': '50',  # Should be int
                'flags': 'ignorecase'  # Should be list
            }
        ]
        
        is_valid, errors = ConfigManager.validate_regex_rules(rules)
        self.assertFalse(is_valid)
        
        # Should have multiple type errors
        self.assertGreater(len(errors), 5)
    
    def test_validate_current_config(self):
        """Test validation of current configuration"""
        # Add some rules to config
        ConfigManager.add_regex_rule('test', 'TEST')
        ConfigManager.add_regex_rule('hello', 'hi', is_regex=False)
        
        # Validate current rules
        is_valid, errors = ConfigManager.validate_regex_rules()
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])


class TestRuleImportExport(unittest.TestCase):
    """Test rule import/export functionality"""
    
    def setUp(self):
        """Set up test environment"""
        ConfigManager.initialize()
        ConfigManager.set_regex_rules([])
    
    def test_export_yaml(self):
        """Test exporting rules to YAML"""
        test_rules = [
            {
                'pattern': 'hello',
                'replacement': 'hi',
                'description': 'Greeting replacement',
                'enabled': True,
                'is_regex': False
            }
        ]
        
        ConfigManager.set_regex_rules(test_rules)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            result = ConfigManager.export_rules_to_file(temp_file, format='yaml')
            self.assertTrue(result)
            
            # Verify file contents
            with open(temp_file, 'r') as f:
                exported_data = yaml.safe_load(f)
            
            self.assertEqual(exported_data, test_rules)
            
        finally:
            os.unlink(temp_file)
    
    def test_export_json(self):
        """Test exporting rules to JSON"""
        test_rules = [
            {
                'pattern': 'test',
                'replacement': 'TEST',
                'enabled': True
            }
        ]
        
        ConfigManager.set_regex_rules(test_rules)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            result = ConfigManager.export_rules_to_file(temp_file, format='json')
            self.assertTrue(result)
            
            # Verify file contents
            with open(temp_file, 'r') as f:
                exported_data = json.load(f)
            
            self.assertEqual(exported_data, test_rules)
            
        finally:
            os.unlink(temp_file)
    
    def test_import_yaml(self):
        """Test importing rules from YAML"""
        test_rules = [
            {
                'pattern': 'import_test',
                'replacement': 'IMPORTED',
                'description': 'Imported rule',
                'enabled': True,
                'is_regex': False,
                'flags': ['ignorecase']
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_rules, f)
            temp_file = f.name
        
        try:
            imported_rules = ConfigManager.import_rules_from_file(temp_file, format='yaml')
            self.assertEqual(imported_rules, test_rules)
            
        finally:
            os.unlink(temp_file)
    
    def test_import_json(self):
        """Test importing rules from JSON"""
        test_rules = [
            {
                'pattern': 'json_test',
                'replacement': 'JSON_IMPORTED',
                'enabled': True
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_rules, f)
            temp_file = f.name
        
        try:
            imported_rules = ConfigManager.import_rules_from_file(temp_file, format='json')
            self.assertEqual(imported_rules, test_rules)
            
        finally:
            os.unlink(temp_file)
    
    def test_import_nonexistent_file(self):
        """Test importing from nonexistent file"""
        with self.assertRaises(FileNotFoundError):
            ConfigManager.import_rules_from_file('/nonexistent/file.yaml')
    
    def test_import_invalid_yaml(self):
        """Test importing invalid YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                ConfigManager.import_rules_from_file(temp_file, format='yaml')
        finally:
            os.unlink(temp_file)
    
    def test_import_invalid_json(self):
        """Test importing invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json content}')
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                ConfigManager.import_rules_from_file(temp_file, format='json')
        finally:
            os.unlink(temp_file)
    
    def test_import_invalid_rule_structure(self):
        """Test importing file with invalid rule structure"""
        invalid_rules = [
            {'pattern': 'test'}  # Missing replacement
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_rules, f)
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                ConfigManager.import_rules_from_file(temp_file, format='yaml')
            
            self.assertIn("Invalid rules format", str(context.exception))
            
        finally:
            os.unlink(temp_file)
    
    def test_export_invalid_rules(self):
        """Test exporting invalid rules"""
        invalid_rules = [
            {'pattern': 123, 'replacement': 'TEST'}  # Invalid pattern type
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                ConfigManager.export_rules_to_file(temp_file, rules=invalid_rules)
            
            self.assertIn("Cannot export invalid rules", str(context.exception))
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestRuleTemplates(unittest.TestCase):
    """Test rule template integration"""
    
    def setUp(self):
        """Set up test environment"""
        ConfigManager.initialize()
    
    def test_get_rule_templates(self):
        """Test getting rule templates"""
        templates = ConfigManager.get_rule_templates()
        
        self.assertIn('templates', templates)
        self.assertIn('combinations', templates)
        
        # Should have our template categories
        self.assertIn('punctuation', templates['templates'])
        self.assertIn('simple_replacements', templates['templates'])
        
        # Should have combinations
        self.assertIn('basic', templates['combinations'])
        self.assertIn('simple', templates['combinations'])


class TestConfigManagerNotInitialized(unittest.TestCase):
    """Test ConfigManager error handling when not initialized"""
    
    def setUp(self):
        """Clear ConfigManager instance"""
        ConfigManager._instance = None
    
    def tearDown(self):
        """Restore ConfigManager"""
        ConfigManager.initialize()
    
    def test_methods_require_initialization(self):
        """Test that methods raise error when not initialized"""
        with self.assertRaises(RuntimeError):
            ConfigManager.get_regex_rules()
        
        with self.assertRaises(RuntimeError):
            ConfigManager.set_regex_rules([])
        
        with self.assertRaises(RuntimeError):
            ConfigManager.add_regex_rule('test', 'TEST')
        
        with self.assertRaises(RuntimeError):
            ConfigManager.remove_regex_rule(0)
        
        with self.assertRaises(RuntimeError):
            ConfigManager.update_regex_rule(0, pattern='test')
        
        with self.assertRaises(RuntimeError):
            ConfigManager.get_regex_processor_enabled()
        
        with self.assertRaises(RuntimeError):
            ConfigManager.set_regex_processor_enabled(True)


if __name__ == '__main__':
    print("Running Regex Configuration Tests")
    print("=" * 38)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)