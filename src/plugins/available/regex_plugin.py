"""
Regex-based text processing plugin
Allows user-defined regex replacements via configuration
"""
import re
from typing import Dict, Any, Optional, List
from plugins.base import ProcessorPlugin
from processing.base import TextProcessor


class RegexProcessor(TextProcessor):
    """Process text using configurable regex rules"""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Initialize with regex rules
        
        Args:
            rules: List of rule dictionaries with pattern, replacement, flags
        """
        self.rules = rules or []
        self.compiled_rules = []
        self._compile_rules()
    
    def _compile_rules(self):
        """Pre-compile regex patterns for efficiency"""
        self.compiled_rules = []
        
        for rule in self.rules:
            if not rule.get('enabled', True):
                continue
                
            pattern = rule.get('pattern', '')
            replacement = rule.get('replacement', '')
            flags_list = rule.get('flags', [])
            
            if not pattern:
                continue
            
            # Convert flag strings to re flags
            flags = 0
            for flag in flags_list:
                flag_lower = flag.lower()
                if flag_lower in ['ignorecase', 'i']:
                    flags |= re.IGNORECASE
                elif flag_lower in ['multiline', 'm']:
                    flags |= re.MULTILINE
                elif flag_lower in ['dotall', 's']:
                    flags |= re.DOTALL
            
            try:
                compiled_pattern = re.compile(pattern, flags)
                self.compiled_rules.append({
                    'pattern': compiled_pattern,
                    'replacement': replacement,
                    'description': rule.get('description', f"Replace {pattern}")
                })
            except re.error as e:
                print(f"Invalid regex pattern '{pattern}': {e}")
    
    def get_name(self) -> str:
        return "RegexProcessor"
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Apply all regex rules to the text"""
        if not text:
            return text
        
        result = text
        for rule in self.compiled_rules:
            try:
                result = rule['pattern'].sub(rule['replacement'], result)
            except Exception as e:
                print(f"Error applying regex rule: {e}")
        
        return result


class RegexPlugin(ProcessorPlugin):
    """Plugin for regex-based text processing"""
    
    def __init__(self):
        self.config = {}
        self.enabled = False
        self.processor = None
    
    def initialize(self, config: Dict[str, Any]):
        """Initialize plugin with configuration"""
        self.config = config
        self.enabled = config.get('enabled', False)
        
        if self.enabled:
            rules = config.get('rules', [])
            if rules:
                self.processor = RegexProcessor(rules)
                print(f"RegexPlugin: Loaded {len(rules)} rules")
            else:
                print("RegexPlugin: No rules configured")
                self.enabled = False
    
    def get_name(self) -> str:
        return "regex_processor"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Applies user-defined regex replacements to transcribed text"
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def get_processor(self):
        return self.processor
    
    def get_priority(self) -> int:
        """Run after basic cleanup but before final formatting"""
        return 30  # Lower than default (50)