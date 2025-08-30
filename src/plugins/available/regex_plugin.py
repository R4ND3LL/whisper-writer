"""
Regex-based text processing plugin
Allows user-defined regex replacements via configuration
Enhanced with performance tracking, priorities, and conditional rules
"""
import re
import time
from typing import Dict, Any, Optional, List
from plugins.base import ProcessorPlugin
from processing.base import TextProcessor


class RegexProcessor(TextProcessor):
    """Process text using configurable regex rules"""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Initialize with regex rules
        
        Args:
            rules: List of rule dictionaries with pattern, replacement, flags, priority, conditions
        """
        self.rules = rules or []
        self.compiled_rules = []
        self.rule_stats = {}  # Track execution time and match counts
        self.performance_tracking = True  # Can be disabled for production
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
            is_regex = rule.get('is_regex', True)  # Default to regex for backward compatibility
            
            if not pattern:
                continue
            
            rule_id = f"rule_{len(self.compiled_rules)}"
            priority = rule.get('priority', 50)  # Default priority
            conditions = rule.get('conditions', {})  # Conditional execution
            
            if is_regex:
                # Handle regex pattern
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
                    elif flag_lower in ['verbose', 'x']:
                        flags |= re.VERBOSE
                    elif flag_lower in ['ascii', 'a']:
                        flags |= re.ASCII
                
                try:
                    compiled_pattern = re.compile(pattern, flags)
                    
                    self.compiled_rules.append({
                        'id': rule_id,
                        'type': 'regex',
                        'pattern': compiled_pattern,
                        'replacement': replacement,
                        'description': rule.get('description', f"Replace regex {pattern}"),
                        'priority': priority,
                        'conditions': conditions,
                        'original_pattern': pattern,  # Keep for debugging
                        'flags': flags_list
                    })
                    
                except re.error as e:
                    print(f"Invalid regex pattern '{pattern}': {e}")
                    continue
                    
            else:
                # Handle plain text replacement
                case_sensitive = True
                for flag in flags_list:
                    if flag.lower() in ['ignorecase', 'i']:
                        case_sensitive = False
                        break
                
                self.compiled_rules.append({
                    'id': rule_id,
                    'type': 'text',
                    'pattern': pattern,
                    'replacement': replacement,
                    'description': rule.get('description', f"Replace text '{pattern}'"),
                    'priority': priority,
                    'conditions': conditions,
                    'original_pattern': pattern,
                    'case_sensitive': case_sensitive
                })
            
            # Initialize stats for this rule
            self.rule_stats[rule_id] = {
                'matches': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        # Sort rules by priority (lower numbers = higher priority)
        self.compiled_rules.sort(key=lambda r: r['priority'])
    
    def get_name(self) -> str:
        return "RegexProcessor"
    
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Apply all regex rules to the text with conditional logic and performance tracking"""
        if not text:
            return text
        
        result = text
        context = context or {}
        
        for rule in self.compiled_rules:
            # Check if rule should be applied based on conditions
            if not self._should_apply_rule(rule, context):
                continue
            
            rule_id = rule['id']
            start_time = time.time() if self.performance_tracking else 0
            
            try:
                if rule['type'] == 'regex':
                    # Apply regex replacement
                    new_result = rule['pattern'].sub(rule['replacement'], result)
                else:
                    # Apply plain text replacement
                    search_text = rule['pattern']
                    replacement_text = rule['replacement']
                    
                    if rule['case_sensitive']:
                        new_result = result.replace(search_text, replacement_text)
                    else:
                        # Case-insensitive text replacement
                        # Find all occurrences and replace them
                        import re as text_re
                        new_result = text_re.sub(
                            text_re.escape(search_text), 
                            replacement_text, 
                            result, 
                            flags=text_re.IGNORECASE
                        )
                
                # Track performance and matches if enabled
                if self.performance_tracking:
                    elapsed_time = time.time() - start_time
                    
                    # Count matches (if text changed)
                    if new_result != result:
                        self.rule_stats[rule_id]['matches'] += 1
                        
                    # Update timing stats
                    stats = self.rule_stats[rule_id]
                    stats['total_time'] += elapsed_time
                    if stats['matches'] > 0:
                        stats['avg_time'] = stats['total_time'] / stats['matches']
                
                result = new_result
                
            except Exception as e:
                rule_type = rule.get('type', 'unknown')
                print(f"Error applying {rule_type} rule {rule_id}: {e}")
        
        return result
    
    def _should_apply_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if a rule should be applied based on conditions"""
        conditions = rule.get('conditions', {})
        
        if not conditions:
            return True  # No conditions = always apply
        
        # Check context-based conditions
        if 'context_contains' in conditions:
            required_keys = conditions['context_contains']
            if not all(key in context for key in required_keys):
                return False
        
        if 'context_values' in conditions:
            for key, expected_value in conditions['context_values'].items():
                if context.get(key) != expected_value:
                    return False
        
        # Add more condition types as needed
        # Examples: time_of_day, recording_mode, window_title, etc.
        
        return True
    
    def get_rule_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all rules"""
        return self.rule_stats.copy()
    
    def reset_statistics(self):
        """Reset all performance statistics"""
        for rule_id in self.rule_stats:
            self.rule_stats[rule_id] = {
                'matches': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
    
    def disable_performance_tracking(self):
        """Disable performance tracking for better runtime performance"""
        self.performance_tracking = False
    
    def enable_performance_tracking(self):
        """Enable performance tracking for debugging and optimization"""
        self.performance_tracking = True
    
    def validate_pattern(self, pattern: str, is_regex: bool = True, flags: List[str] = None) -> tuple[bool, str]:
        """
        Validate a pattern (regex or text) without adding it to the processor
        
        Returns:
            tuple: (is_valid, error_message or success_message)
        """
        if not pattern:
            return False, "Pattern cannot be empty"
        
        if not is_regex:
            # Text patterns are always valid (any string can be searched)
            return True, f"Text pattern '{pattern}' is valid"
        
        try:
            # Convert flags if provided
            re_flags = 0
            if flags:
                for flag in flags:
                    flag_lower = flag.lower()
                    if flag_lower in ['ignorecase', 'i']:
                        re_flags |= re.IGNORECASE
                    elif flag_lower in ['multiline', 'm']:
                        re_flags |= re.MULTILINE
                    elif flag_lower in ['dotall', 's']:
                        re_flags |= re.DOTALL
                    elif flag_lower in ['verbose', 'x']:
                        re_flags |= re.VERBOSE
                    elif flag_lower in ['ascii', 'a']:
                        re_flags |= re.ASCII
                    else:
                        return False, f"Unknown flag: {flag}"
            
            # Try to compile the pattern
            re.compile(pattern, re_flags)
            return True, f"Regex pattern '{pattern}' is valid"
            
        except re.error as e:
            return False, f"Invalid regex pattern: {str(e)}"
    
    def test_rule(self, pattern: str, replacement: str, test_text: str, is_regex: bool = True, flags: List[str] = None) -> Dict[str, Any]:
        """
        Test a rule against sample text without modifying the processor
        
        Returns:
            dict with test results including matches, result text, and performance
        """
        # First validate the pattern
        is_valid, message = self.validate_pattern(pattern, is_regex, flags)
        if not is_valid:
            return {
                'valid': False,
                'error': message,
                'original': test_text,
                'result': test_text,
                'matches': 0,
                'execution_time': 0,
                'type': 'regex' if is_regex else 'text'
            }
        
        try:
            start_time = time.time()
            
            if is_regex:
                # Convert flags
                re_flags = 0
                if flags:
                    for flag in flags:
                        flag_lower = flag.lower()
                        if flag_lower in ['ignorecase', 'i']:
                            re_flags |= re.IGNORECASE
                        elif flag_lower in ['multiline', 'm']:
                            re_flags |= re.MULTILINE
                        elif flag_lower in ['dotall', 's']:
                            re_flags |= re.DOTALL
                        elif flag_lower in ['verbose', 'x']:
                            re_flags |= re.VERBOSE
                        elif flag_lower in ['ascii', 'a']:
                            re_flags |= re.ASCII
                
                # Compile and test the pattern
                compiled_pattern = re.compile(pattern, re_flags)
                
                # Find all matches before replacement
                matches = list(compiled_pattern.finditer(test_text))
                
                # Apply replacement
                result_text = compiled_pattern.sub(replacement, test_text)
                
                match_details = [(m.group(), m.start(), m.end()) for m in matches]
                
            else:
                # Plain text replacement
                case_sensitive = True
                if flags:
                    for flag in flags:
                        if flag.lower() in ['ignorecase', 'i']:
                            case_sensitive = False
                            break
                
                if case_sensitive:
                    # Count matches manually for case-sensitive text
                    matches_count = test_text.count(pattern)
                    result_text = test_text.replace(pattern, replacement)
                    
                    # Find match positions
                    match_details = []
                    start = 0
                    while True:
                        pos = test_text.find(pattern, start)
                        if pos == -1:
                            break
                        match_details.append((pattern, pos, pos + len(pattern)))
                        start = pos + 1
                else:
                    # Case-insensitive text replacement
                    import re as text_re
                    escaped_pattern = text_re.escape(pattern)
                    
                    # Find matches
                    matches = list(text_re.finditer(escaped_pattern, test_text, flags=text_re.IGNORECASE))
                    match_details = [(m.group(), m.start(), m.end()) for m in matches]
                    matches_count = len(matches)
                    
                    # Apply replacement
                    result_text = text_re.sub(escaped_pattern, replacement, test_text, flags=text_re.IGNORECASE)
            
            execution_time = time.time() - start_time
            
            return {
                'valid': True,
                'original': test_text,
                'result': result_text,
                'matches': len(match_details) if is_regex else matches_count,
                'match_details': match_details,
                'execution_time': execution_time,
                'changed': result_text != test_text,
                'type': 'regex' if is_regex else 'text'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'original': test_text,
                'result': test_text,
                'matches': 0,
                'execution_time': 0,
                'type': 'regex' if is_regex else 'text'
            }


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