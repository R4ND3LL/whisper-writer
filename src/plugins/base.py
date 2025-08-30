"""
Base classes for the plugin system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Plugin(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """
        Initialize plugin with configuration
        
        Args:
            config: Plugin-specific configuration from config.yaml
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Return plugin name (should match config key)
        
        Returns:
            Plugin identifier name
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        Return plugin version
        
        Returns:
            Version string (e.g., "1.0.0")
        """
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Check if plugin is enabled
        
        Returns:
            True if plugin should be active
        """
        pass
    
    def get_description(self) -> str:
        """
        Return plugin description (optional)
        
        Returns:
            Human-readable description
        """
        return ""


class ProcessorPlugin(Plugin):
    """Base class for text processing plugins"""
    
    @abstractmethod
    def get_processor(self):
        """
        Return the TextProcessor instance for this plugin
        
        Returns:
            TextProcessor instance or None if disabled
        """
        pass
    
    def get_priority(self) -> int:
        """
        Return processing priority (lower = earlier in pipeline)
        
        Returns:
            Priority value (default 50)
        """
        return 50