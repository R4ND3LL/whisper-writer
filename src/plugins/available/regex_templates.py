"""
Rule templates for common regex replacements
Provides predefined rule sets for different use cases
"""
from typing import Dict, List, Any

# Common rule templates organized by category
COMMON_RULES = {
    'punctuation': {
        'name': 'Punctuation Fixes',
        'description': 'Convert spoken punctuation to symbols',
        'rules': [
            {
                'pattern': r'\bperiod\b',
                'replacement': '.',
                'description': 'Convert "period" to .',
                'enabled': True,
                'priority': 20
            },
            {
                'pattern': r'\bcomma\b', 
                'replacement': ',',
                'description': 'Convert "comma" to ,',
                'enabled': True,
                'priority': 20
            },
            {
                'pattern': r'\bquestion mark\b',
                'replacement': '?',
                'description': 'Convert "question mark" to ?',
                'enabled': True,
                'priority': 20
            },
            {
                'pattern': r'\bexclamation point\b',
                'replacement': '!',
                'description': 'Convert "exclamation point" to !',
                'enabled': True,
                'priority': 20
            },
            {
                'pattern': r'\bsemicolon\b',
                'replacement': ';',
                'description': 'Convert "semicolon" to ;',
                'enabled': True,
                'priority': 20
            },
            {
                'pattern': r'\bcolon\b',
                'replacement': ':',
                'description': 'Convert "colon" to :',
                'enabled': True,
                'priority': 20
            }
        ]
    },
    
    'programming': {
        'name': 'Programming Terms',
        'description': 'Convert spoken programming symbols',
        'rules': [
            {
                'pattern': r'\bopen paren\b',
                'replacement': '(',
                'description': 'Convert "open paren" to (',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bclose paren\b',
                'replacement': ')',
                'description': 'Convert "close paren" to )',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bopen brace\b',
                'replacement': '{',
                'description': 'Convert "open brace" to {',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bclose brace\b',
                'replacement': '}',
                'description': 'Convert "close brace" to }',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bopen bracket\b',
                'replacement': '[',
                'description': 'Convert "open bracket" to [',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bclose bracket\b',
                'replacement': ']',
                'description': 'Convert "close bracket" to ]',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bforward slash\b',
                'replacement': '/',
                'description': 'Convert "forward slash" to /',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bbackslash\b',
                'replacement': '\\\\',
                'description': 'Convert "backslash" to \\',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bpipe\b',
                'replacement': '|',
                'description': 'Convert "pipe" to |',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bampersand\b',
                'replacement': '&',
                'description': 'Convert "ampersand" to &',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bequals\b',
                'replacement': '=',
                'description': 'Convert "equals" to =',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bplus\b',
                'replacement': '+',
                'description': 'Convert "plus" to +',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bminus\b',
                'replacement': '-',
                'description': 'Convert "minus" to -',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\basterisk\b',
                'replacement': '*',
                'description': 'Convert "asterisk" to *',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': r'\bsemicolon\b',
                'replacement': ';',
                'description': 'Convert "semicolon" to ;',
                'enabled': True,
                'priority': 25
            }
        ]
    },
    
    'formatting': {
        'name': 'Text Formatting',
        'description': 'Handle spacing and formatting commands',
        'rules': [
            {
                'pattern': r'\bnew line\b',
                'replacement': '\n',
                'description': 'Convert "new line" to line break',
                'enabled': True,
                'priority': 30
            },
            {
                'pattern': r'\btab\b',
                'replacement': '\t',
                'description': 'Convert "tab" to tab character',
                'enabled': True,
                'priority': 30
            },
            {
                'pattern': r'\bdouble space\b',
                'replacement': '  ',
                'description': 'Convert "double space" to two spaces',
                'enabled': True,
                'priority': 30
            },
            {
                'pattern': r'\bno space\b',
                'replacement': '',
                'description': 'Remove "no space" and surrounding spaces',
                'enabled': True,
                'priority': 30
            }
        ]
    },
    
    'simple_replacements': {
        'name': 'Simple Text Replacements',
        'description': 'Easy find-and-replace without regex complexity',
        'rules': [
            {
                'pattern': 'forward slash',
                'replacement': '/',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "forward slash" with /',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'back slash',
                'replacement': '\\\\',  # Need to escape the backslash in the replacement
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "back slash" with \\',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'at sign',
                'replacement': '@',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "at sign" with @',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'hash tag',
                'replacement': '#',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "hash tag" with #',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'dollar sign',
                'replacement': '$',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "dollar sign" with $',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'percent sign',
                'replacement': '%',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "percent sign" with %',
                'enabled': True,
                'priority': 25
            },
            {
                'pattern': 'new line',
                'replacement': '\n',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "new line" with line break (simple)',
                'enabled': True,
                'priority': 30
            },
            {
                'pattern': 'tab character',
                'replacement': '\t',
                'is_regex': False,
                'flags': ['ignorecase'],
                'description': 'Replace "tab character" with tab',
                'enabled': True,
                'priority': 30
            }
        ]
    },
    
    'speech_cleanup': {
        'name': 'Speech Cleanup',
        'description': 'Remove filler words and fix speech artifacts',
        'rules': [
            {
                'pattern': r'(?i)\bum+\b\s*',
                'replacement': '',
                'description': 'Remove filler word "um", "umm", "ummm", etc.',
                'enabled': True,
                'priority': 10
            },
            {
                'pattern': r'(?i)\buh+\b\s*',
                'replacement': '',
                'description': 'Remove filler word "uh", "uhh", "uhhh", etc.',
                'enabled': True,
                'priority': 10
            },
            {
                'pattern': r'\byou know\b',
                'replacement': '',
                'description': 'Remove "you know" filler',
                'enabled': True,
                'priority': 10
            },
            {
                'pattern': r'\blike\b(?=\s)',
                'replacement': '',
                'description': 'Remove "like" when used as filler',
                'enabled': False,  # Disabled by default as it might be too aggressive
                'priority': 10
            },
            {
                'pattern': r'\s+',
                'replacement': ' ',
                'description': 'Normalize multiple spaces to single space',
                'enabled': True,
                'priority': 80  # Run late to clean up after other rules
            }
        ]
    },
    
    'numbers': {
        'name': 'Number Formatting',
        'description': 'Convert spoken numbers to digits',
        'rules': [
            {
                'pattern': r'\bzero\b',
                'replacement': '0',
                'description': 'Convert "zero" to 0',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bone\b',
                'replacement': '1',
                'description': 'Convert "one" to 1',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\btwo\b',
                'replacement': '2',
                'description': 'Convert "two" to 2',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bthree\b',
                'replacement': '3',
                'description': 'Convert "three" to 3',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bfour\b',
                'replacement': '4',
                'description': 'Convert "four" to 4',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bfive\b',
                'replacement': '5',
                'description': 'Convert "five" to 5',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bsix\b',
                'replacement': '6',
                'description': 'Convert "six" to 6',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bseven\b',
                'replacement': '7',
                'description': 'Convert "seven" to 7',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\beight\b',
                'replacement': '8',
                'description': 'Convert "eight" to 8',
                'enabled': True,
                'priority': 40
            },
            {
                'pattern': r'\bnine\b',
                'replacement': '9',
                'description': 'Convert "nine" to 9',
                'enabled': True,
                'priority': 40
            }
        ]
    },
    
    'medical': {
        'name': 'Medical Terminology',
        'description': 'Common medical transcription fixes',
        'rules': [
            {
                'pattern': r'\bmg\b',
                'replacement': 'mg',
                'description': 'Ensure "mg" is lowercase',
                'flags': ['ignorecase'],
                'enabled': True,
                'priority': 50
            },
            {
                'pattern': r'\bml\b',
                'replacement': 'ml',
                'description': 'Ensure "ml" is lowercase', 
                'flags': ['ignorecase'],
                'enabled': True,
                'priority': 50
            },
            {
                'pattern': r'\bcc\b',
                'replacement': 'cc',
                'description': 'Ensure "cc" is lowercase',
                'flags': ['ignorecase'],
                'enabled': True,
                'priority': 50
            }
        ]
    }
}


def get_template_categories() -> List[str]:
    """Get list of available template categories"""
    return list(COMMON_RULES.keys())


def get_template(category: str) -> Dict[str, Any]:
    """Get template by category name"""
    return COMMON_RULES.get(category, {})


def get_template_rules(category: str) -> List[Dict[str, Any]]:
    """Get just the rules from a template category"""
    template = get_template(category)
    return template.get('rules', [])


def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """Get all available templates"""
    return COMMON_RULES.copy()


def create_combined_template(categories: List[str], name: str = None, description: str = None) -> Dict[str, Any]:
    """
    Combine multiple template categories into a single template
    
    Args:
        categories: List of category names to combine
        name: Optional name for combined template
        description: Optional description for combined template
        
    Returns:
        Combined template dictionary
    """
    combined_rules = []
    combined_categories = []
    
    for category in categories:
        if category in COMMON_RULES:
            combined_rules.extend(COMMON_RULES[category]['rules'])
            combined_categories.append(category)
    
    # Sort by priority to maintain order
    combined_rules.sort(key=lambda r: r.get('priority', 50))
    
    return {
        'name': name or f"Combined Template ({', '.join(combined_categories)})",
        'description': description or f"Combined rules from: {', '.join(combined_categories)}",
        'rules': combined_rules,
        'categories': combined_categories
    }


def get_common_combinations() -> Dict[str, Dict[str, Any]]:
    """Get pre-defined useful combinations of templates"""
    return {
        'basic': create_combined_template(
            ['speech_cleanup', 'punctuation'],
            'Basic Cleanup',
            'Essential speech cleanup and punctuation fixes'
        ),
        
        'simple': create_combined_template(
            ['speech_cleanup', 'simple_replacements'],
            'Simple Mode',
            'Easy text replacements for non-technical users'
        ),
        
        'programming': create_combined_template(
            ['speech_cleanup', 'punctuation', 'programming', 'formatting'],
            'Programming Assistant',
            'Complete set for coding dictation'
        ),
        
        'writing': create_combined_template(
            ['speech_cleanup', 'punctuation', 'formatting', 'numbers'],
            'General Writing',
            'Optimized for document writing and note-taking'
        ),
        
        'medical': create_combined_template(
            ['speech_cleanup', 'punctuation', 'medical', 'numbers'],
            'Medical Transcription',
            'Specialized for medical dictation'
        )
    }


def export_template_to_config(template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export a template in the format expected by config.yaml
    
    Returns:
        Dictionary ready for the plugins.regex_processor section
    """
    return {
        'enabled': True,
        'rules': template.get('rules', [])
    }


def validate_template(template: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a template structure
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(template, dict):
        errors.append("Template must be a dictionary")
        return False, errors
    
    if 'rules' not in template:
        errors.append("Template must have 'rules' key")
        return False, errors
    
    if not isinstance(template['rules'], list):
        errors.append("Template 'rules' must be a list")
        return False, errors
    
    # Validate each rule
    for i, rule in enumerate(template['rules']):
        if not isinstance(rule, dict):
            errors.append(f"Rule {i} must be a dictionary")
            continue
            
        if 'pattern' not in rule:
            errors.append(f"Rule {i} missing 'pattern' field")
            
        if 'replacement' not in rule:
            errors.append(f"Rule {i} missing 'replacement' field")
    
    return len(errors) == 0, errors