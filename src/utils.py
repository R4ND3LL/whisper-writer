import yaml
import os

class ConfigManager:
    _instance = None

    def __init__(self):
        """Initialize the ConfigManager instance."""
        self.config = None
        self.schema = None

    @classmethod
    def initialize(cls, schema_path=None):
        """Initialize the ConfigManager with the given schema path."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.schema = cls._instance.load_config_schema(schema_path)
            cls._instance.config = cls._instance.load_default_config()
            cls._instance.load_user_config()
            cls._add_default_regex_rules()

    @classmethod
    def get_schema(cls):
        """Get the configuration schema."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        return cls._instance.schema
    
    @classmethod
    def get_config(cls):
        """Get the full configuration dictionary."""
        if cls._instance is None:
            return None
        return cls._instance.config
    
    # For backward compatibility
    @classmethod
    def get_full_config(cls):
        """Alias for get_config."""
        return cls.get_config()

    @classmethod
    def get_config_section(cls, *keys):
        """Get a specific section of the configuration."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")

        section = cls._instance.config
        for key in keys:
            if isinstance(section, dict) and key in section:
                section = section[key]
            else:
                return {}
        return section

    @classmethod
    def get_config_value(cls, *keys):
        """Get a specific configuration value using nested keys."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")

        value = cls._instance.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    @classmethod
    def set_config_value(cls, value, *keys):
        """Set a specific configuration value using nested keys."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")

        config = cls._instance.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

    @staticmethod
    def load_config_schema(schema_path=None):
        """Load the configuration schema from a YAML file."""
        if schema_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(base_dir, 'config_schema.yaml')

        with open(schema_path, 'r') as file:
            schema = yaml.safe_load(file)
        return schema

    def load_default_config(self):
        """Load default configuration values from the schema."""
        def extract_value(item):
            if isinstance(item, dict):
                if 'value' in item:
                    return item['value']
                else:
                    return {k: extract_value(v) for k, v in item.items()}
            return item

        config = {}
        for category, settings in self.schema.items():
            config[category] = extract_value(settings)
        return config

    def load_user_config(self, config_path=os.path.join('src', 'config.yaml')):
        """Load user configuration and merge with default config."""
        def deep_update(source, overrides):
            for key, value in overrides.items():
                if isinstance(value, dict) and key in source:
                    deep_update(source[key], value)
                else:
                    source[key] = value

        if config_path and os.path.isfile(config_path):
            try:
                with open(config_path, 'r') as file:
                    user_config = yaml.safe_load(file)
                    deep_update(self.config, user_config)
            except yaml.YAMLError:
                print("Error in configuration file. Using default configuration.")

    @classmethod
    def save_config(cls, config_path=os.path.join('src', 'config.yaml')):
        """Save the current configuration to a YAML file."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        with open(config_path, 'w') as file:
            yaml.dump(cls._instance.config, file, default_flow_style=False)

    @classmethod
    def reload_config(cls):
        """
        Reload the configuration from the file.
        """
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        cls._instance.config = cls._instance.load_default_config()
        cls._instance.load_user_config()

    @classmethod
    def config_file_exists(cls):
        """Check if a valid config file exists."""
        config_path = os.path.join('src', 'config.yaml')
        return os.path.isfile(config_path)

    @classmethod
    def console_print(cls, message):
        """Print a message to the console if enabled in the configuration."""
        if cls._instance and cls._instance.config['misc']['print_to_terminal']:
            print(message)

    # Regex rule management methods
    @classmethod
    def get_regex_rules(cls):
        """Get the list of regex replacement rules."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        return cls.get_config_section('plugins', 'regex_processor', 'rules') or []
    
    @classmethod
    def set_regex_rules(cls, rules):
        """Set the list of regex replacement rules."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        cls.set_config_value(rules, 'plugins', 'regex_processor', 'rules')
    
    @classmethod
    def get_regex_processor_enabled(cls):
        """Check if regex processor plugin is enabled."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        return cls.get_config_value('plugins', 'regex_processor', 'enabled') or False
    
    @classmethod
    def set_regex_processor_enabled(cls, enabled):
        """Enable or disable the regex processor plugin."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        cls.set_config_value(enabled, 'plugins', 'regex_processor', 'enabled')
    
    @classmethod
    def add_regex_rule(cls, pattern, replacement, description=None, enabled=True, 
                       is_regex=True, flags=None, priority=50, conditions=None):
        """Add a new regex rule to the configuration."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        
        rule = {
            'pattern': pattern,
            'replacement': replacement,
            'enabled': enabled,
            'is_regex': is_regex,
            'priority': priority
        }
        
        if description:
            rule['description'] = description
        if flags:
            rule['flags'] = flags
        if conditions:
            rule['conditions'] = conditions
        
        rules = cls.get_regex_rules()
        rules.append(rule)
        cls.set_regex_rules(rules)
        return rule
    
    @classmethod
    def remove_regex_rule(cls, rule_index):
        """Remove a regex rule by index."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        
        rules = cls.get_regex_rules()
        if 0 <= rule_index < len(rules):
            removed_rule = rules.pop(rule_index)
            cls.set_regex_rules(rules)
            return removed_rule
        else:
            raise IndexError("Rule index out of range")
    
    @classmethod
    def update_regex_rule(cls, rule_index, **updates):
        """Update a regex rule by index."""
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized")
        
        rules = cls.get_regex_rules()
        if 0 <= rule_index < len(rules):
            rules[rule_index].update(updates)
            cls.set_regex_rules(rules)
            return rules[rule_index]
        else:
            raise IndexError("Rule index out of range")
    
    @classmethod
    def validate_regex_rules(cls, rules=None):
        """Validate regex rules structure and return validation results."""
        if rules is None:
            rules = cls.get_regex_rules()
        
        if not isinstance(rules, list):
            return False, ["Rules must be a list"]
        
        errors = []
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                errors.append(f"Rule {i}: Must be an object/dictionary")
                continue
                
            if 'pattern' not in rule:
                errors.append(f"Rule {i}: Missing required 'pattern' field")
            elif not isinstance(rule['pattern'], str):
                errors.append(f"Rule {i}: 'pattern' must be a string")
                
            if 'replacement' not in rule:
                errors.append(f"Rule {i}: Missing required 'replacement' field")
            elif not isinstance(rule['replacement'], str):
                errors.append(f"Rule {i}: 'replacement' must be a string")
            
            # Validate optional fields
            if 'enabled' in rule and not isinstance(rule['enabled'], bool):
                errors.append(f"Rule {i}: 'enabled' must be boolean")
                
            if 'is_regex' in rule and not isinstance(rule['is_regex'], bool):
                errors.append(f"Rule {i}: 'is_regex' must be boolean")
                
            if 'priority' in rule and not isinstance(rule['priority'], int):
                errors.append(f"Rule {i}: 'priority' must be integer")
                
            if 'flags' in rule and not isinstance(rule['flags'], list):
                errors.append(f"Rule {i}: 'flags' must be a list")
        
        return len(errors) == 0, errors
    
    @classmethod
    def import_rules_from_file(cls, file_path, format='yaml'):
        """Import regex rules from a file."""
        import json
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r') as file:
                if format.lower() == 'json':
                    imported_rules = json.load(file)
                else:  # yaml
                    imported_rules = yaml.safe_load(file)
            
            # Validate imported rules
            is_valid, errors = cls.validate_regex_rules(imported_rules)
            if not is_valid:
                raise ValueError(f"Invalid rules format: {'; '.join(errors)}")
            
            return imported_rules
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to parse {format.upper()} file: {str(e)}")
    
    @classmethod
    def export_rules_to_file(cls, file_path, rules=None, format='yaml'):
        """Export regex rules to a file."""
        import json
        
        if rules is None:
            rules = cls.get_regex_rules()
        
        # Validate rules before export
        is_valid, errors = cls.validate_regex_rules(rules)
        if not is_valid:
            raise ValueError(f"Cannot export invalid rules: {'; '.join(errors)}")
        
        try:
            with open(file_path, 'w') as file:
                if format.lower() == 'json':
                    json.dump(rules, file, indent=2)
                else:  # yaml
                    yaml.dump(rules, file, default_flow_style=False)
            
            return True
            
        except Exception as e:
            raise IOError(f"Failed to write {format.upper()} file: {str(e)}")
    
    @classmethod
    def get_rule_templates(cls):
        """Get available rule templates from the templates module."""
        try:
            from plugins.available.regex_templates import get_all_templates, get_common_combinations
            return {
                'templates': get_all_templates(),
                'combinations': get_common_combinations()
            }
        except ImportError:
            return {'templates': {}, 'combinations': {}}

    @classmethod
    def _add_default_regex_rules(cls):
        """Add default regex rules for common model hallucinations."""
        existing_rules = cls.get_regex_rules()
        
        # Check if underscore rule already exists
        for rule in existing_rules:
            if 'underscore' in rule.get('description', '').lower():
                return  # Rule already exists
        
        # Add aggressive underscore removal pattern
        cls.add_regex_rule(
            pattern=r'_+',  # Match any sequence of 1 or more underscores
            replacement='',
            description='Remove all underscore sequences from model hallucinations',
            enabled=True,
            is_regex=True,
            priority=1
        )

    @classmethod
    def verbose_print(cls, message: str):
        """Print debug message only if verbose logging is enabled."""
        if not cls._instance:
            return
        enabled = cls.get_config_value('misc', 'verbose_logging')
        if enabled:
            print(message)

    @classmethod
    def get_audio_debug_folder(cls):
        """Get the folder path for saving debug audio files."""
        import os
        
        # Get configured path (default: "debug_audio")
        configured_path = cls.get_config_value('misc', 'audio_debug_folder')
        
        # Handle None case (fallback to default)
        if configured_path is None:
            configured_path = 'debug_audio'
        
        # If it's an absolute path, use it directly
        if os.path.isabs(configured_path):
            debug_folder = configured_path
        else:
            # Relative path: make it relative to WhisperWriter project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            debug_folder = os.path.join(project_root, configured_path)
        
        os.makedirs(debug_folder, exist_ok=True)
        return debug_folder

    @classmethod
    def is_audio_debug_enabled(cls):
        """Check if audio debug saving is enabled."""
        if not cls._instance:
            return False
        enabled = cls.get_config_value('misc', 'save_audio_debug')
        # Handle None case (default to False)
        if enabled is None:
            return False
        return bool(enabled)
